from django.urls import path
from . import views_dashboard

urlpatterns = [
    path("groups/<uuid:group_id>/learners/", views_dashboard.DashboardLearnersView.as_view(), name="dashboard_learners"),
    path("groups/<uuid:group_id>/learners/<uuid:learner_id>/timeline/", views_dashboard.DashboardTimelineView.as_view(), name="dashboard_timeline"),
    path("groups/<uuid:group_id>/competences/", views_dashboard.DashboardCompetencesView.as_view(), name="dashboard_competences"),
]
