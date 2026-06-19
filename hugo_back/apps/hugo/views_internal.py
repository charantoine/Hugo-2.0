"""Internal: verbatim-window (prep B), rag/search."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import HugoSession, HugoMessage
from .services.evaluation_trace_pivot import enrich_trace_payload_with_pivot
from .services.tracing import build_turn_review_payload, tracing_enabled
from .services.session_observability import build_session_observability_snapshot
from apps.library.models import RagCitation
from apps.referentials.access_control import (
    is_admin_like,
    is_tutor_like,
    tutor_linked_groups_for_learner,
)


class VerbatimWindowView(generics.GenericAPIView):
    """GET /internal/learners/{learner_id}/verbatim-window — RBAC by share; not used by default."""
    permission_classes = [IsAuthenticated]

    def get(self, request, learner_id):
        limit = int(request.query_params.get("limit_messages", 20))
        is_self = str(request.user.id) == str(learner_id)
        if not is_self and not is_tutor_like(request.user) and not is_admin_like(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        sessions = HugoSession.objects.filter(
            learner_id=learner_id,
            organisation_id=request.user.organisation_id,
        )
        if not is_self:
            if is_tutor_like(request.user):
                allowed_group_ids = tutor_linked_groups_for_learner(
                    tutor_id=request.user.id,
                    learner_id=learner_id,
                    organisation_id=request.user.organisation_id,
                )
                if not allowed_group_ids:
                    return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
                sessions = sessions.filter(group_id__in=allowed_group_ids)
            sessions = sessions.filter(share_verbatim=True)
        messages = HugoMessage.objects.filter(
            session__in=sessions,
        ).order_by("-created_at")[:limit]
        return Response({
            "messages": [
                {"id": str(m.id), "role": m.role, "created_at": m.created_at.isoformat()}
                for m in messages
            ]
        })


class RagSearchView(APIView):
    """POST /internal/rag/search — question-driven retrieval (for Hugo)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get("query", "")
        group_id = request.data.get("group_id")
        top_k = int(request.data.get("top_k", 20))
        if not query or not group_id:
            return Response({"detail": "query and group_id required."}, status=status.HTTP_400_BAD_REQUEST)
        from apps.library.models import GroupDocument, DocumentChunk
        from apps.referentials.models import Group
        Group.objects.get(id=group_id, organisation_id=request.user.organisation_id)
        gds = GroupDocument.objects.filter(
            group_id=group_id,
            organisation_id=request.user.organisation_id,
            status=GroupDocument.Status.ACTIVE,
        ).values_list("document_id", flat=True)
        chunks = DocumentChunk.objects.filter(document_id__in=gds)[:top_k]
        return Response({
            "chunks": [
                {"id": str(c.id), "document_id": str(c.document_id), "content_preview": c.content[:200]}
                for c in chunks
            ]
        })


class TurnReviewView(APIView):
    """GET /internal/hugo/sessions/{session_id}/turn-review — review latest or selected turn debug payload."""
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        if not tracing_enabled():
            return Response({"detail": "Debug tracing disabled."}, status=status.HTTP_404_NOT_FOUND)

        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=request.user.organisation_id,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        is_self = str(request.user.id) == str(session.learner_id)
        if not is_self and not is_admin_like(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        assistant_message_id = request.query_params.get("assistant_message_id")
        assistant_qs = session.messages.filter(role=HugoMessage.Role.ASSISTANT).order_by("-created_at")
        if assistant_message_id:
            assistant_qs = assistant_qs.filter(id=assistant_message_id)
        assistant_message = assistant_qs.first()
        if not assistant_message:
            return Response({"detail": "No assistant turn found."}, status=status.HTTP_404_NOT_FOUND)

        learner_message = (
            session.messages.filter(
                role=HugoMessage.Role.LEARNER,
                created_at__lte=assistant_message.created_at,
            )
            .order_by("-created_at")
            .first()
        )
        if not learner_message:
            return Response({"detail": "No learner turn found."}, status=status.HTTP_404_NOT_FOUND)

        rag_citations = RagCitation.objects.filter(message=assistant_message).order_by("-created_at")
        return Response(
            build_turn_review_payload(
                session=session,
                learner_message=learner_message,
                assistant_message=assistant_message,
                rag_citations=rag_citations,
            )
        )


class SessionPilotageView(APIView):
    """GET /internal/hugo/sessions/{session_id}/pilotage — product-safe pilotage snapshot."""
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=request.user.organisation_id,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        is_self = str(request.user.id) == str(session.learner_id)
        if not is_self and not is_tutor_like(request.user) and not is_admin_like(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        if not is_self and is_tutor_like(request.user):
            allowed_group_ids = tutor_linked_groups_for_learner(
                tutor_id=request.user.id,
                learner_id=session.learner_id,
                organisation_id=request.user.organisation_id,
            )
            if session.group_id not in allowed_group_ids:
                return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        learner_message = (
            session.messages.filter(role=HugoMessage.Role.LEARNER)
            .order_by("-created_at")
            .first()
        )
        if not learner_message:
            return Response({"detail": "No learner turn found."}, status=status.HTTP_404_NOT_FOUND)

        payload = learner_message.llm_request_payload or {}
        return Response(
            {
                "session": {
                    "id": str(session.id),
                    "current_phase": session.current_phase,
                    "manual_phase_override": session.manual_phase_override,
                },
                "conversation_profile": payload.get("conversation_profile", "reflective_afest"),
                "conversation_progress": payload.get("conversation_progress", {}),
                "ui_state": payload.get("ui_state", {}),
                "session_memory": payload.get("session_memory", {}),
                "conversation_decision": payload.get("conversation_decision", {}),
            }
        )


class SessionObservabilityView(APIView):
    """GET /internal/hugo/sessions/{session_id}/observability — signaux techniques admin/debug."""

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        if not is_admin_like(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=request.user.organisation_id,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(build_session_observability_snapshot(session))
