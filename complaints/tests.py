import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Complaint


class ComplaintViewsTests(TestCase):
    def test_map_and_create_pages_load(self):
        User.objects.create_user(username="ali", password="StrongPass123")
        self.client.login(username="ali", password="StrongPass123")

        map_response = self.client.get(reverse("complaints:map"))
        create_response = self.client.get(reverse("complaints:create"))

        self.assertEqual(map_response.status_code, 200)
        self.assertEqual(create_response.status_code, 200)

    def test_complaint_data_returns_active_complaints(self):
        Complaint.objects.create(
            title="Bozuk sokak lambası",
            description="Park girişindeki lamba yanmıyor.",
            category=Complaint.Category.LIGHTING,
            latitude="41.008200",
            longitude="28.978400",
        )
        Complaint.objects.create(
            title="Çözülmüş bildirim",
            description="Bu kayıt haritada görünmemeli.",
            category=Complaint.Category.OTHER,
            latitude="41.010000",
            longitude="28.980000",
            status=Complaint.Status.RESOLVED,
        )

        response = self.client.get(reverse("complaints:data"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["complaints"]), 1)
        self.assertEqual(response.json()["complaints"][0]["category"], "lighting")

    def test_staff_panel_requires_authorized_user(self):
        response = self.client.get(reverse("complaints:panel"))
        self.assertEqual(response.status_code, 302)

        User.objects.create_user(username="standart", password="StrongPass123")
        self.client.login(username="standart", password="StrongPass123")
        response = self.client.get(reverse("complaints:panel"))
        self.assertEqual(response.status_code, 302)

        User.objects.create_user(username="admin", password="StrongPass123", is_staff=True)
        self.client.login(username="admin", password="StrongPass123")
        response = self.client.get(reverse("complaints:panel"))
        self.assertEqual(response.status_code, 200)

    def test_mobile_api_post_requires_authorization(self):
        response = self.client.post(
            reverse("complaints:mobile_api"),
            data=json.dumps({
                "title": "Yetkisiz bildirim",
                "description": "Bu kayıt reddedilmeli.",
                "category": Complaint.Category.OTHER,
                "latitude": "41.008200",
                "longitude": "28.978400",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_mobile_api_post_accepts_logged_in_user(self):
        User.objects.create_user(username="mobil", password="StrongPass123")
        self.client.login(username="mobil", password="StrongPass123")

        response = self.client.post(
            reverse("complaints:mobile_api"),
            data=json.dumps({
                "title": "Mobil API bildirimi",
                "description": "Uygulama dersinden gelen kayıt.",
                "category": Complaint.Category.ROAD,
                "latitude": "41.008200",
                "longitude": "28.978400",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Complaint.objects.filter(title="Mobil API bildirimi").exists())

    def test_mobile_register_and_login_return_token(self):
        register_response = self.client.post(
            reverse("complaints:mobile_register"),
            data=json.dumps({
                "username": "flutter",
                "email": "flutter@example.com",
                "password": "StrongPass123",
                "phone": "5551112233",
            }),
            content_type="application/json",
        )

        self.assertEqual(register_response.status_code, 201)
        self.assertIn("token", register_response.json())

        login_response = self.client.post(
            reverse("complaints:mobile_login"),
            data=json.dumps({"username": "flutter", "password": "StrongPass123"}),
            content_type="application/json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.json())

    def test_mobile_token_allows_crud(self):
        user = User.objects.create_user(username="tokenuser", password="StrongPass123")
        login_response = self.client.post(
            reverse("complaints:mobile_login"),
            data=json.dumps({"username": "tokenuser", "password": "StrongPass123"}),
            content_type="application/json",
        )
        token = login_response.json()["token"]

        create_response = self.client.post(
            reverse("complaints:mobile_api"),
            data=json.dumps({
                "title": "Token kaydı",
                "description": "Token ile eklendi.",
                "category": Complaint.Category.WATER,
                "latitude": "41.008200",
                "longitude": "28.978400",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        self.assertEqual(create_response.status_code, 201)
        complaint_id = create_response.json()["complaint"]["id"]

        update_response = self.client.patch(
            reverse("complaints:mobile_api_detail", args=[complaint_id]),
            data=json.dumps({
                "title": "Token kaydı güncel",
                "description": "Token ile güncellendi.",
                "category": Complaint.Category.WATER,
                "latitude": "41.008200",
                "longitude": "28.978400",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["complaint"]["title"], "Token kaydı güncel")

        delete_response = self.client.delete(
            reverse("complaints:mobile_api_detail", args=[complaint_id]),
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Complaint.objects.filter(id=complaint_id).exists())

    def test_mobile_panel_requires_staff_token(self):
        User.objects.create_user(username="notstaff", password="StrongPass123")
        login_response = self.client.post(
            reverse("complaints:mobile_login"),
            data=json.dumps({"username": "notstaff", "password": "StrongPass123"}),
            content_type="application/json",
        )
        token = login_response.json()["token"]

        response = self.client.get(
            reverse("complaints:mobile_panel_api"),
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 403)

        User.objects.create_user(username="staffapi", password="StrongPass123", is_staff=True)
        staff_login = self.client.post(
            reverse("complaints:mobile_login"),
            data=json.dumps({"username": "staffapi", "password": "StrongPass123"}),
            content_type="application/json",
        )
        staff_token = staff_login.json()["token"]
        response = self.client.get(
            reverse("complaints:mobile_panel_api"),
            HTTP_AUTHORIZATION=f"Token {staff_token}",
        )
        self.assertEqual(response.status_code, 200)

# Create your tests here.
