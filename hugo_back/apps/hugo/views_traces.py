"""Traces: validate."""
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import Trace, LearnerState
from apps.quality.views import log_audit
from apps.referentials.access_control import can_access_learner_in_group


class ValidateTraceView(APIView):
    """POST /traces/{trace_id}/validate."""
    permission_classes = [IsAuthenticated]

    def post(self, request, trace_id):
        trace = Trace.objects.filter(
            id=trace_id,
            organisation_id=request.user.organisation_id,
        ).first()
        if not trace:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if not can_access_learner_in_group(
            user=request.user,
            learner_id=trace.session.learner_id,
            group_id=trace.session.group_id,
            organisation_id=request.user.organisation_id,
        ):
            raise PermissionDenied("You are not allowed to validate this trace.")
        trace.validated_by = request.user
        trace.validated_at = timezone.now()
        trace.save()
        log_audit(request, "trace_validated", "trace", trace.id)
        LearnerState.objects.update_or_create(
            organisation_id=request.user.organisation_id,
            learner_id=trace.session.learner_id,
            group_id=trace.session.group_id,
            defaults={
                "skills_matrix": {},
                "missing_coverage": [],
                "open_action_items": [],
                "summary": "",
            },
        )
        return Response({
            "id": str(trace.id),
            "validated_by": str(trace.validated_by_id),
            "validated_at": trace.validated_at.isoformat(),
        })
