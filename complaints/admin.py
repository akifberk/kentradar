from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "created_by", "created_at", "is_resolved")
    list_filter = ("category", "status", "is_resolved", "created_at")
    search_fields = ("title", "description", "reporter_name")
    readonly_fields = ("created_at",)
