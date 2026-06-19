# Dashboard: learners per group, timeline, competences
from django.db.models import OuterRef, Prefetch, Subquery
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.referentials.models import Group, GroupMembership
from apps.referentials.access_control import (
    can_access_learner_in_group,
    learner_ids_visible_in_group,
)
from .models import HugoSession, HugoMessage, Trace, LearnerState


def _pilotage_from_learner_payload(payload):
    """
    Résumé compact et produit-safe pour la vue tuteur.
    """
    if not isinstance(payload, dict) or not payload:
        return None
    ts = payload.get("turn_state") if isinstance(payload.get("turn_state"), dict) else {}
    dec = payload.get("conversation_decision") if isinstance(payload.get("conversation_decision"), dict) else {}
    progress = payload.get("conversation_progress") if isinstance(payload.get("conversation_progress"), dict) else {}
    session_memory = payload.get("session_memory") if isinstance(payload.get("session_memory"), dict) else {}
    if not ts and not dec and not progress:
        return None

    def _s(val, default=""):
        return default if val is None else val

    return {
        "conversation_profile": _s(payload.get("conversation_profile"), "reflective_afest"),
        "active_objective": _s(progress.get("active_objective"), _s(dec.get("primary_intent"), "")),
        "current_step_label": _s(progress.get("current_step_label"), ""),
        "progress_percent": progress.get("percent"),
        "can_summarize": bool(progress.get("can_summarize")),
        "decision_move": _s(dec.get("pedagogical_move"), ""),
        "closure_signal": _s(ts.get("closure_signal"), "none"),
        "learner_help_request": _s(ts.get("learner_help_request"), "none"),
        "loop_risk": _s(ts.get("loop_risk"), "low"),
        "reason_codes": list(progress.get("reason_codes") or dec.get("reason_codes") or [])[:3],
        "carry_over_points": list(session_memory.get("carry_over_points") or [])[:2],
    }


def _dashboard_first_learner_message_preview(text):
    stripped = str(text or "").strip()
    if len(stripped) > 120:
        return stripped[:117] + "..."
    return stripped


def _dashboard_timeline_message_dict(message):
    row = {
        "id": str(message.id),
        "role": message.role,
        "content": message.content,
        "assistant_display_variants": (
            message.assistant_display_variants if message.role == HugoMessage.Role.ASSISTANT else {}
        ),
        "created_at": message.created_at.isoformat(),
    }
    if message.role == HugoMessage.Role.LEARNER:
        pilotage = _pilotage_from_learner_payload(getattr(message, "llm_request_payload", None) or {})
        if pilotage is not None:
            row["pilotage"] = pilotage
    return row


class DashboardLearnersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        get_object_or_404(Group, id=group_id, organisation_id=request.user.organisation_id)
        visible_ids = learner_ids_visible_in_group(
            user=request.user,
            group_id=group_id,
            organisation_id=request.user.organisation_id,
        )
        members = GroupMembership.objects.filter(
            group_id=group_id,
            organisation_id=request.user.organisation_id,
            user_id__in=visible_ids,
        ).select_related("user")
        return Response({
            "learners": [
                {"id": str(m.user_id), "username": m.user.username}
                for m in members
            ]
        })


class DashboardTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id, learner_id):
        get_object_or_404(Group, id=group_id, organisation_id=request.user.organisation_id)
        if not can_access_learner_in_group(
            user=request.user,
            learner_id=learner_id,
            group_id=group_id,
            organisation_id=request.user.organisation_id,
        ):
            raise PermissionDenied("You are not allowed to access this learner.")
        first_learner_message_subquery = (
            HugoMessage.objects.filter(
                session_id=OuterRef("pk"),
                role=HugoMessage.Role.LEARNER,
            )
            .order_by("created_at")
            .values("content")[:1]
        )
        sessions = HugoSession.objects.filter(
            group_id=group_id,
            learner_id=learner_id,
            organisation_id=request.user.organisation_id,
        ).annotate(first_learner_message_text=Subquery(first_learner_message_subquery)).prefetch_related(
            Prefetch(
                "messages",
                queryset=HugoMessage.objects.order_by("created_at"),
            )
        ).order_by("-created_at")[:50]
        traces = Trace.objects.filter(
            session__group_id=group_id,
            session__learner_id=learner_id,
            organisation_id=request.user.organisation_id,
        ).order_by("-created_at")[:50]
        return Response({
            "sessions": [
                {
                    "id": str(s.id),
                    "created_at": s.created_at.isoformat(),
                    "first_learner_message": (
                        _dashboard_first_learner_message_preview(
                            getattr(s, "first_learner_message_text", "")
                        )
                        if s.share_verbatim
                        else ""
                    ),
                    "share_verbatim": s.share_verbatim,
                    "messages": [
                        _dashboard_timeline_message_dict(m)
                        for m in s.messages.all()
                    ] if s.share_verbatim else [],
                }
                for s in sessions
            ],
            "traces": [{"id": str(t.id), "created_at": t.created_at.isoformat(), "validated_at": t.validated_at.isoformat() if t.validated_at else None} for t in traces],
        })


class DashboardCompetencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        get_object_or_404(Group, id=group_id, organisation_id=request.user.organisation_id)
        visible_ids = learner_ids_visible_in_group(
            user=request.user,
            group_id=group_id,
            organisation_id=request.user.organisation_id,
        )
        states = LearnerState.objects.filter(
            group_id=group_id,
            organisation_id=request.user.organisation_id,
            learner_id__in=visible_ids,
        )
        return Response({
            "competences": [
                {"learner_id": str(s.learner_id), "summary": s.summary, "skills_matrix": s.skills_matrix}
                for s in states
            ]
        })
