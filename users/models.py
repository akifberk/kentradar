from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        STANDARD = "standard", "Standart Kullanici"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STANDARD)
    phone = models.CharField("Telefon", max_length=20, blank=True)

    class Meta:
        verbose_name = "Kullanici profili"
        verbose_name_plural = "Kullanici profilleri"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
