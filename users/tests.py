from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class RegisterTests(TestCase):
    def test_register_creates_standard_user_profile(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "veli",
                "email": "veli@example.com",
                "phone": "5551112233",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="veli")
        self.assertEqual(user.profile.role, UserProfile.Role.STANDARD)
        self.assertEqual(user.profile.phone, "5551112233")

# Create your tests here.
