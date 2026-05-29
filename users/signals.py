from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if hasattr(instance, "profile"):
        return

    role = UserProfile.Role.ADMIN if instance.is_staff else UserProfile.Role.STANDARD
    UserProfile.objects.create(user=instance, role=role)
