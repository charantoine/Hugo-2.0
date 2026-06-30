from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.DocumentUploadView.as_view(), name="document_upload"),
    path("", views.DocumentListCreate.as_view(), name="document_list_create"),
    path("<uuid:document_id>/index/", views.DocumentIndexView.as_view(), name="document_index"),
    path("<uuid:document_id>/", views.DocumentRetrieveUpdate.as_view(), name="document_detail"),
]
