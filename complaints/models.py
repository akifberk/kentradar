from django.db import models
from django.urls import reverse


class Complaint(models.Model):
    class Category(models.TextChoices):
        ROAD = "road", "Yol / kaldırım"
        WATER = "water", "Su / kanalizasyon"
        LIGHTING = "lighting", "Aydınlatma"
        WASTE = "waste", "Çöp / temizlik"
        PARK = "park", "Park / yeşil alan"
        OTHER = "other", "Diğer"

    class Status(models.TextChoices):
        OPEN = "open", "Açık"
        IN_PROGRESS = "in_progress", "İşlemde"
        RESOLVED = "resolved", "Çözüldü"

    CATEGORY_COLORS = {
        Category.ROAD: "#f97316",
        Category.WATER: "#0ea5e9",
        Category.LIGHTING: "#eab308",
        Category.WASTE: "#22c55e",
        Category.PARK: "#16a34a",
        Category.OTHER: "#8b5cf6",
    }

    title = models.CharField("Başlık", max_length=120)
    description = models.TextField("Açıklama")
    category = models.CharField(
        "Sorun türü",
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    photo = models.ImageField("Fotoğraf", upload_to="complaints/", blank=True)
    latitude = models.DecimalField("Enlem", max_digits=9, decimal_places=6)
    longitude = models.DecimalField("Boylam", max_digits=9, decimal_places=6)
    reporter_name = models.CharField("Bildiren kişi", max_length=80, blank=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="complaints",
        blank=True,
        null=True,
        verbose_name="Kaydı oluşturan",
    )
    status = models.CharField("Durum", max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField("Bildirim zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("Güncelleme zamanı", auto_now=True)
    is_resolved = models.BooleanField("Çözüldü", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Şikayet"
        verbose_name_plural = "Şikayetler"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("complaints:map")

    @property
    def color(self):
        return self.CATEGORY_COLORS.get(self.category, self.CATEGORY_COLORS[self.Category.OTHER])

    def save(self, *args, **kwargs):
        self.is_resolved = self.status == self.Status.RESOLVED
        super().save(*args, **kwargs)
