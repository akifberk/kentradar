import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import ComplaintForm, ComplaintStaffForm, ReportFilterForm
from .models import Complaint


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
def complaint_api(request):
    if request.method == "GET":
        complaints = Complaint.objects.all()
        return JsonResponse({"complaints": [serialize_complaint(complaint) for complaint in complaints]})

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Gecersiz JSON."}, status=400)

        form = ComplaintForm(payload)
        if form.is_valid():
            complaint = form.save(commit=False)
            if request.user.is_authenticated:
                complaint.created_by = request.user
            complaint.save()
            return JsonResponse({"complaint": serialize_complaint(complaint)}, status=201)

        return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"error": "Bu method desteklenmiyor."}, status=405)


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
