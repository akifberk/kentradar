from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


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


class MobileAuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mobile_tokens")
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mobil API token"
        verbose_name_plural = "Mobil API tokenleri"

    def __str__(self):
        return f"{self.user.username} token"

    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(user=user, key=get_random_string(64))
