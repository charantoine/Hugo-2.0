from django.urls import path
from . import views_internal, views_internal_analytics

urlpatterns = [
    path("learners/<uuid:learner_id>/verbatim-window/", views_internal.VerbatimWindowView.as_view(), name="verbatim_window"),
    path("rag/search/", views_internal.RagSearchView.as_view(), name="rag_search"),
    path("hugo/sessions/<uuid:session_id>/turn-review/", views_internal.TurnReviewView.as_view(), name="turn_review"),
    path("hugo/sessions/<uuid:session_id>/pilotage/", views_internal.SessionPilotageView.as_view(), name="session_pilotage"),
    path("hugo/sessions/<uuid:session_id>/observability/", views_internal.SessionObservabilityView.as_view(), name="session_observability"),
    path("hugo/sessions/<uuid:session_id>/d9bis/build/", views_internal_analytics.D9bisBuildView.as_view(), name="d9bis_build"),
    path("hugo/sessions/<uuid:session_id>/d9bis/export/", views_internal_analytics.D9bisExportView.as_view(), name="d9bis_export"),
    path("hugo/analytics/conversation-summary/", views_internal_analytics.ConversationSummaryView.as_view(), name="conversation_summary"),
]
