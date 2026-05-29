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
    path("api/mobile/register/", views.mobile_register, name="mobile_register"),
    path("api/mobile/login/", views.mobile_login, name="mobile_login"),
    path("api/mobile/logout/", views.mobile_logout, name="mobile_logout"),
    path("api/mobile/password-reset/", views.mobile_password_reset, name="mobile_password_reset"),
    path("api/mobile/complaints/", views.complaint_api, name="mobile_api"),
    path("api/mobile/complaints/<int:pk>/", views.complaint_api_detail, name="mobile_api_detail"),
    path("api/mobile/panel/", views.mobile_panel_api, name="mobile_panel_api"),
    path("api/mobile/report/", views.mobile_report_api, name="mobile_report_api"),
]
