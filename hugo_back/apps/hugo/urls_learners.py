from django.urls import path
from . import views_learners

urlpatterns = [
    path("sessions/", views_learners.LearnerSessionList.as_view(), name="learner_sessions"),
    path("traces/", views_learners.LearnerTraceList.as_view(), name="learner_traces"),
    path("evidence/", views_learners.LearnerEvidenceList.as_view(), name="learner_evidence"),
]
