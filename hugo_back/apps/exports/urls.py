from django.urls import path

from .views import ExportDownloadView, ExportRunView


urlpatterns = [
    path("run/", ExportRunView.as_view(), name="exports_run"),
    path("download/<uuid:run_id>/", ExportDownloadView.as_view(), name="exports_download"),
]
