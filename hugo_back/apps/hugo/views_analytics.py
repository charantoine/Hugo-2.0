from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.hugo.analytics.cohort_dashboard import get_cohort_metrics, get_per_learner_progress


class CohortMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 30) or 30)
        return Response(get_cohort_metrics(str(request.user.organisation_id), days))


class LearnerProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, learner_id):
        return Response(
            {
                "learner_id": str(learner_id),
                "progress": get_per_learner_progress(str(request.user.organisation_id), str(learner_id)),
            }
        )
