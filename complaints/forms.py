from django import forms

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            "title",
            "description",
            "category",
            "photo",
            "latitude",
            "longitude",
            "reporter_name",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Orn. Kaldirimda cukur var"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Sorunu kisaca anlatin"}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*", "capture": "environment"}),
            "latitude": forms.NumberInput(attrs={"step": "any", "inputmode": "decimal"}),
            "longitude": forms.NumberInput(attrs={"step": "any", "inputmode": "decimal"}),
            "reporter_name": forms.TextInput(attrs={"placeholder": "Istege bagli"}),
        }

    def clean_latitude(self):
        latitude = self.cleaned_data["latitude"]
        if not -90 <= latitude <= 90:
            raise forms.ValidationError("Enlem -90 ile 90 arasinda olmalidir.")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data["longitude"]
        if not -180 <= longitude <= 180:
            raise forms.ValidationError("Boylam -180 ile 180 arasinda olmalidir.")
        return longitude


class ComplaintStaffForm(ComplaintForm):
    class Meta(ComplaintForm.Meta):
        fields = ComplaintForm.Meta.fields + ["status"]


class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        label="Baslangic tarihi",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = forms.DateField(
        required=False,
        label="Bitis tarihi",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    category = forms.ChoiceField(required=False, label="Kategori")
    status = forms.ChoiceField(required=False, label="Durum")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [("", "Tum kategoriler")] + list(Complaint.Category.choices)
        self.fields["status"].choices = [("", "Tum durumlar")] + list(Complaint.Status.choices)
