from django.urls import path
from . import views

urlpatterns = [
    path("qualiopi/evidence-bundle/", views.EvidenceBundleView.as_view(), name="evidence_bundle"),
]
