from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.complaint_map, name="map"),
    path("bildir/", views.complaint_create, name="create"),
    path("sikayet/<int:pk>/", views.complaint_detail, name="detail"),
    path("sikayet/<int:pk>/duzenle/", views.complaint_update, name="update"),
    path("sikayet/<int:pk>/sil/", views.complaint_delete, name="delete"),
    path("panel/", views.panel, name="panel"),
    path("rapor/", views.report, name="report"),
    path("api/sikayetler/", views.complaint_data, name="data"),
    path("api/mobile/complaints/", views.complaint_api, name="mobile_api"),
]
