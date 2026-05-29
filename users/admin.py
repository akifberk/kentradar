from django.contrib import admin

from .models import MobileAuthToken, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "phone")


@admin.register(MobileAuthToken)
class MobileAuthTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email", "key")
    readonly_fields = ("key", "created_at")
