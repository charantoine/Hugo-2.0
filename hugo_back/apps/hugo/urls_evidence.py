from django.urls import path
from . import views_evidence

urlpatterns = [
    path("", views_evidence.EvidenceCreateView.as_view(), name="evidence_create"),
]
