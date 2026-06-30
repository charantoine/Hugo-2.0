from django.urls import path
from . import views_traces

urlpatterns = [
    path("<uuid:trace_id>/validate/", views_traces.ValidateTraceView.as_view(), name="validate_trace"),
]
