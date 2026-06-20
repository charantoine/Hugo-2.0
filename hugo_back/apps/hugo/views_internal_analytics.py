"""Internal analytics endpoints — D9bis & observabilité avancée v1 (SUPERADMIN)."""
from __future__ import annotations
from app_core.tenant_context import tenant_organisation_id

import json
from datetime import date

from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.hugo.models import HugoSession
from apps.hugo.services.d9bis_analytics import (
    build_or_refresh_d9bis_for_session,
    serialize_session_analysis,
)
from apps.hugo.services.observability_advanced_v1 import build_conversation_summary
from apps.referentials.access_control import is_superadmin


class D9bisBuildView(APIView):
    """POST /internal/hugo/sessions/{session_id}/d9bis/build/ — persist derived D9bis artefacts."""

    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        if not is_superadmin(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        aggregate = build_or_refresh_d9bis_for_session(session)
        return Response(
            {
                "status": "built",
                "session_analysis_id": str(aggregate.id),
                "turn_analyses_count": aggregate.turn_analyses_count,
            },
            status=status.HTTP_201_CREATED,
        )


class D9bisExportView(APIView):
    """GET /internal/hugo/sessions/{session_id}/d9bis/export/ — JSON export technique."""

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        if not is_superadmin(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
        ).select_related("llm_analysis").first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        aggregate = getattr(session, "llm_analysis", None)
        if aggregate is None:
            aggregate = build_or_refresh_d9bis_for_session(session)

        payload = serialize_session_analysis(aggregate, include_turns=True)
        if request.query_params.get("download") == "1":
            content = json.dumps(payload, ensure_ascii=False, indent=2)
            response = HttpResponse(content, content_type="application/json; charset=utf-8")
            response["Content-Disposition"] = (
                f'attachment; filename="d9bis_session_{session_id}.json"'
            )
            return response
        return Response(payload)


class ConversationSummaryView(APIView):
    """GET /internal/hugo/analytics/conversation-summary/ — agrégats org/groupe."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_superadmin(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        group_id = request.query_params.get("group_id")
        from_date_raw = request.query_params.get("from")
        to_date_raw = request.query_params.get("to")

        from_date = None
        to_date = None
        try:
            if from_date_raw:
                from_date = date.fromisoformat(str(from_date_raw))
            if to_date_raw:
                to_date = date.fromisoformat(str(to_date_raw))
        except ValueError:
            return Response(
                {"detail": "from/to must be ISO dates YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = build_conversation_summary(
            organisation_id=tenant_organisation_id(request),
            group_id=str(group_id) if group_id else None,
            from_date=from_date,
            to_date=to_date,
        )
        if request.query_params.get("download") == "1":
            content = json.dumps(payload, ensure_ascii=False, indent=2)
            response = HttpResponse(content, content_type="application/json; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="conversation_summary_v1.json"'
            return response
        return Response(payload)
