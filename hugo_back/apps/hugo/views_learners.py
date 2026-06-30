"""Learner history: sessions, traces, evidence (with filters)."""
from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from app_core.tenant_context import tenant_organisation_id

from .models import HugoSession, Trace, Evidence
from .serializers import HugoSessionSerializer, TraceSerializer, EvidenceSerializer


class LearnerSessionList(generics.ListAPIView):
    """GET /learners/sessions?from=&to=&competence_item_ids= — own sessions."""
    serializer_class = HugoSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = HugoSession.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
            learner=self.request.user,
        )
        from_ = self.request.query_params.get("from")
        to_ = self.request.query_params.get("to")
        if from_:
            try:
                qs = qs.filter(created_at__gte=timezone.datetime.fromisoformat(from_.replace("Z", "+00:00")))
            except Exception:
                pass
        if to_:
            try:
                qs = qs.filter(created_at__lte=timezone.datetime.fromisoformat(to_.replace("Z", "+00:00")))
            except Exception:
                pass
        return qs.order_by("-created_at")


class LearnerTraceList(generics.ListAPIView):
    """GET /learners/traces?from=&to=&competence_item_ids= — own traces."""
    serializer_class = TraceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Trace.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
            session__learner=self.request.user,
        )
        from_ = self.request.query_params.get("from")
        to_ = self.request.query_params.get("to")
        if from_:
            try:
                qs = qs.filter(created_at__gte=timezone.datetime.fromisoformat(from_.replace("Z", "+00:00")))
            except Exception:
                pass
        if to_:
            try:
                qs = qs.filter(created_at__lte=timezone.datetime.fromisoformat(to_.replace("Z", "+00:00")))
            except Exception:
                pass
        item_ids = self.request.query_params.get("competence_item_ids")
        if item_ids:
            ids = [x.strip() for x in item_ids.split(",") if x.strip()]
            if ids:
                qs = qs.filter(referential_item_id__in=ids)
        return qs.order_by("-created_at")


class LearnerEvidenceList(generics.ListAPIView):
    """GET /learners/evidence — own evidence."""
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Evidence.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
        ).filter(
            models.Q(trace__session__learner=self.request.user)
            | models.Q(session__learner=self.request.user)
        ).order_by("-created_at")
