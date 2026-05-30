import json
import os

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import ComplaintForm, ComplaintStaffForm, ReportFilterForm
from .models import Complaint
from users.models import MobileAuthToken, UserProfile


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def can_manage_complaint(user, complaint):
    return user.is_staff or complaint.created_by_id == user.id


def serialize_complaint(complaint):
    return {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "category_label": complaint.get_category_display(),
        "status": complaint.status,
        "status_label": complaint.get_status_display(),
        "color": complaint.color,
        "latitude": float(complaint.latitude),
        "longitude": float(complaint.longitude),
        "photo_url": complaint.photo.url if complaint.photo else "",
        "created_at": complaint.created_at.strftime("%d.%m.%Y %H:%M"),
    }


def parse_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8")) if request.body else {}
        except json.JSONDecodeError:
            return None
    return request.POST


def serialize_user(user):
    role = getattr(getattr(user, "profile", None), "role", UserProfile.Role.ADMIN if user.is_staff else UserProfile.Role.STANDARD)
    profile = getattr(user, "profile", None)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "role": role,
        "phone": profile.phone if profile else "",
        "is_active": user.is_active,
        "date_joined": user.date_joined.strftime("%d.%m.%Y"),
    }


def mobile_user(request):
    if request.user.is_authenticated:
        return request.user

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Token "):
        key = auth_header.removeprefix("Token ").strip()
        token = MobileAuthToken.objects.select_related("user").filter(key=key).first()
        if token:
            return token.user

    return None


def mobile_api_allowed(request):
    api_key = os.environ.get("MOBILE_API_KEY")
    if mobile_user(request):
        return True
    if api_key and request.headers.get("X-API-Key") == api_key:
        return True
    return False


def mobile_staff_required(request):
    user = mobile_user(request)
    return user if user and user.is_staff else None


def complaint_map(request):
    complaints = Complaint.objects.filter(is_resolved=False)
    legend = [
        {"label": label, "color": Complaint.CATEGORY_COLORS[value]}
        for value, label in Complaint.Category.choices
    ]
    return render(
        request,
        "complaints/map.html",
        {
            "complaints": complaints,
            "legend": legend,
        },
    )


@login_required
def complaint_create(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.created_by = request.user
            if not complaint.reporter_name:
                complaint.reporter_name = request.user.get_username()
            complaint.save()
            messages.success(request, "Sikayetiniz haritaya eklendi.")
            return redirect("complaints:detail", pk=complaint.pk)
    else:
        form = ComplaintForm()

    return render(request, "complaints/create.html", {"form": form})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not can_manage_complaint(request.user, complaint):
        return HttpResponseForbidden("Bu kaydi goruntuleme yetkiniz yok.")
    return render(request, "complaints/detail.html", {"complaint": complaint})


@login_required
def complaint_update(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not can_manage_complaint(request.user, complaint):
        return HttpResponseForbidden("Bu kaydi guncelleme yetkiniz yok.")

    form_class = ComplaintStaffForm if request.user.is_staff else ComplaintForm
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, "Sikayet guncellendi.")
            return redirect("complaints:detail", pk=complaint.pk)
    else:
        form = form_class(instance=complaint)

    return render(request, "complaints/update.html", {"form": form, "complaint": complaint})


@login_required
def complaint_delete(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not can_manage_complaint(request.user, complaint):
        return HttpResponseForbidden("Bu kaydi silme yetkiniz yok.")

    if request.method == "POST":
        complaint.delete()
        messages.success(request, "Sikayet silindi.")
        return redirect("complaints:panel" if request.user.is_staff else "complaints:map")

    return render(request, "complaints/delete.html", {"complaint": complaint})


def complaint_data(request):
    complaints = Complaint.objects.filter(is_resolved=False)
    data = [serialize_complaint(complaint) for complaint in complaints]
    return JsonResponse({"complaints": data})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def complaint_api(request):
    if request.method == "GET":
        complaints = Complaint.objects.all()
        return JsonResponse({"complaints": [serialize_complaint(complaint) for complaint in complaints]})

    if not mobile_api_allowed(request):
        return JsonResponse({"error": "API icin giris veya gecerli X-API-Key gerekli."}, status=403)

    if request.method == "POST":
        payload = parse_payload(request)
        if payload is None:
            return JsonResponse({"error": "Gecersiz JSON."}, status=400)

        form = ComplaintForm(payload, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            user = mobile_user(request)
            if user:
                complaint.created_by = user
                if not complaint.reporter_name:
                    complaint.reporter_name = user.get_username()
            complaint.save()
            return JsonResponse({"complaint": serialize_complaint(complaint)}, status=201)

        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Bu method desteklenmiyor."}, status=405)


@csrf_exempt
@require_http_methods(["POST"])
def mobile_register(request):
    payload = parse_payload(request)
    if payload is None:
        return JsonResponse({"error": "Gecersiz JSON."}, status=400)

    username = payload.get("username", "").strip()
    email = payload.get("email", "").strip()
    password = payload.get("password", "")
    phone = payload.get("phone", "").strip()

    if not username or not email or not password:
        return JsonResponse({"error": "Kullanici adi, e-posta ve sifre zorunlu."}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "Sifre en az 8 karakter olmalidir."}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Bu kullanici adi kullaniliyor."}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Bu e-posta kullaniliyor."}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    UserProfile.objects.update_or_create(
        user=user,
        defaults={"role": UserProfile.Role.STANDARD, "phone": phone},
    )
    token = MobileAuthToken.create_for_user(user)
    return JsonResponse({"token": token.key, "user": serialize_user(user)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def mobile_login(request):
    payload = parse_payload(request)
    if payload is None:
        return JsonResponse({"error": "Gecersiz JSON."}, status=400)

    username = payload.get("username", "").strip()
    password = payload.get("password", "")
    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"error": "Kullanici adi veya sifre hatali."}, status=400)

    token = MobileAuthToken.create_for_user(user)
    return JsonResponse({"token": token.key, "user": serialize_user(user)})


@csrf_exempt
@require_http_methods(["POST"])
def mobile_logout(request):
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Token "):
        MobileAuthToken.objects.filter(key=auth_header.removeprefix("Token ").strip()).delete()
    return JsonResponse({"success": True})


@csrf_exempt
@require_http_methods(["POST"])
def mobile_password_reset(request):
    payload = parse_payload(request)
    if payload is None:
        return JsonResponse({"error": "Gecersiz JSON."}, status=400)

    form = PasswordResetForm({"email": payload.get("email", "")})
    if form.is_valid():
        form.save(request=request)
        return JsonResponse({"success": True})
    return JsonResponse({"errors": form.errors}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def complaint_api_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if request.method == "GET":
        return JsonResponse({"complaint": serialize_complaint(complaint)})

    user = mobile_user(request)
    if not user or not can_manage_complaint(user, complaint):
        return JsonResponse({"error": "Bu islem icin yetkiniz yok."}, status=403)

    if request.method == "DELETE":
        complaint.delete()
        return JsonResponse({"success": True})

    payload = parse_payload(request)
    if payload is None:
        return JsonResponse({"error": "Gecersiz JSON."}, status=400)

    form_class = ComplaintStaffForm if user.is_staff else ComplaintForm
    data = {
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "reporter_name": complaint.reporter_name,
    }
    if user.is_staff:
        data["status"] = complaint.status
    data.update(payload)

    form = form_class(data, request.FILES, instance=complaint)
    if form.is_valid():
        complaint = form.save()
        return JsonResponse({"complaint": serialize_complaint(complaint)})
    return JsonResponse({"errors": form.errors}, status=400)


@require_http_methods(["GET"])
def mobile_panel_api(request):
    user = mobile_staff_required(request)
    if not user:
        return JsonResponse({"error": "Yetkili kullanici gerekli."}, status=403)

    category_counts = list(
        Complaint.objects.values("category").annotate(total=Count("id")).order_by("category")
    )
    return JsonResponse(
        {
            "total_complaints": Complaint.objects.count(),
            "open_complaints": Complaint.objects.filter(status=Complaint.Status.OPEN).count(),
            "resolved_complaints": Complaint.objects.filter(status=Complaint.Status.RESOLVED).count(),
            "user_count": User.objects.count(),
            "category_chart": {
                "labels": [Complaint.Category(item["category"]).label for item in category_counts],
                "data": [item["total"] for item in category_counts],
            },
            "latest_complaints": [
                serialize_complaint(complaint)
                for complaint in Complaint.objects.select_related("created_by")[:10]
            ],
        }
    )


@require_http_methods(["GET"])
def mobile_report_api(request):
    user = mobile_staff_required(request)
    if not user:
        return JsonResponse({"error": "Yetkili kullanici gerekli."}, status=403)

    complaints = Complaint.objects.select_related("created_by").all()
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    category = request.GET.get("category")
    status = request.GET.get("status")

    if start_date:
        complaints = complaints.filter(created_at__date__gte=start_date)
    if end_date:
        complaints = complaints.filter(created_at__date__lte=end_date)
    if category:
        complaints = complaints.filter(category=category)
    if status:
        complaints = complaints.filter(status=status)

    return JsonResponse(
        {
            "total": complaints.count(),
            "complaints": [serialize_complaint(complaint) for complaint in complaints],
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def mobile_users_api(request):
    user = mobile_staff_required(request)
    if not user:
        return JsonResponse({"error": "Yetkili kullanici gerekli."}, status=403)

    users = User.objects.select_related("profile").order_by("username")
    return JsonResponse({"users": [serialize_user(item) for item in users]})


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def mobile_user_detail_api(request, pk):
    staff = mobile_staff_required(request)
    if not staff:
        return JsonResponse({"error": "Yetkili kullanici gerekli."}, status=403)

    target = get_object_or_404(User.objects.select_related("profile"), pk=pk)
    if request.method == "DELETE":
        if target.id == staff.id:
            return JsonResponse({"error": "Kendi hesabinizi silemezsiniz."}, status=400)
        target.delete()
        return JsonResponse({"success": True})

    payload = parse_payload(request)
    if payload is None:
        return JsonResponse({"error": "Gecersiz JSON."}, status=400)

    if "is_staff" in payload:
        target.is_staff = bool(payload["is_staff"])
        target.save(update_fields=["is_staff"])

    if "role" in payload:
        profile, _ = UserProfile.objects.get_or_create(user=target)
        profile.role = payload["role"]
        profile.save(update_fields=["role"])

    if "is_active" in payload:
        target.is_active = bool(payload["is_active"])
        target.save(update_fields=["is_active"])

    target.refresh_from_db()
    return JsonResponse({"user": serialize_user(target)})


@user_passes_test(is_staff_user)
def panel(request):
    category_counts = list(
        Complaint.objects.values("category").annotate(total=Count("id")).order_by("category")
    )
    status_counts = list(
        Complaint.objects.values("status").annotate(total=Count("id")).order_by("status")
    )
    monthly_counts = list(
        Complaint.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    context = {
        "total_complaints": Complaint.objects.count(),
        "open_complaints": Complaint.objects.filter(status=Complaint.Status.OPEN).count(),
        "resolved_complaints": Complaint.objects.filter(status=Complaint.Status.RESOLVED).count(),
        "user_count": User.objects.count(),
        "latest_complaints": Complaint.objects.select_related("created_by")[:8],
        "category_chart": {
            "labels": [Complaint.Category(item["category"]).label for item in category_counts],
            "data": [item["total"] for item in category_counts],
            "colors": [Complaint.CATEGORY_COLORS[item["category"]] for item in category_counts],
        },
        "status_chart": {
            "labels": [Complaint.Status(item["status"]).label for item in status_counts],
            "data": [item["total"] for item in status_counts],
        },
        "monthly_chart": {
            "labels": [item["month"].strftime("%m.%Y") for item in monthly_counts if item["month"]],
            "data": [item["total"] for item in monthly_counts if item["month"]],
        },
    }
    return render(request, "complaints/panel.html", context)


@user_passes_test(is_staff_user)
def report(request):
    form = ReportFilterForm(request.GET or None)
    complaints = Complaint.objects.select_related("created_by").all()

    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        category = form.cleaned_data.get("category")
        status = form.cleaned_data.get("status")

        if start_date:
            complaints = complaints.filter(created_at__date__gte=start_date)
        if end_date:
            complaints = complaints.filter(created_at__date__lte=end_date)
        if category:
            complaints = complaints.filter(category=category)
        if status:
            complaints = complaints.filter(status=status)

    return render(
        request,
        "complaints/report.html",
        {
            "form": form,
            "complaints": complaints,
            "total": complaints.count(),
        },
    )
