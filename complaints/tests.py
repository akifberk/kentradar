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
            title="Bozuk sokak lambasi",
            description="Park girisindeki lamba yanmiyor.",
            category=Complaint.Category.LIGHTING,
            latitude="41.008200",
            longitude="28.978400",
        )
        Complaint.objects.create(
            title="Cozulmus bildirim",
            description="Bu kayit haritada gorunmemeli.",
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
            data={
                "title": "Yetkisiz bildirim",
                "description": "Bu kayit reddedilmeli.",
                "category": Complaint.Category.OTHER,
                "latitude": "41.008200",
                "longitude": "28.978400",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_mobile_api_post_accepts_logged_in_user(self):
        User.objects.create_user(username="mobil", password="StrongPass123")
        self.client.login(username="mobil", password="StrongPass123")

        response = self.client.post(
            reverse("complaints:mobile_api"),
            data={
                "title": "Mobil API bildirimi",
                "description": "Uygulama dersinden gelen kayit.",
                "category": Complaint.Category.ROAD,
                "latitude": "41.008200",
                "longitude": "28.978400",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Complaint.objects.filter(title="Mobil API bildirimi").exists())

# Create your tests here.
