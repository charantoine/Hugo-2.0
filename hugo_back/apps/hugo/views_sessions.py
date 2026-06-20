"""Hugo sessions: create, get, messages, generate-trace, share."""
from __future__ import annotations
from app_core.tenant_context import tenant_organisation_id

import json
import re
import logging
from typing import Optional
from django.http import StreamingHttpResponse
from django.db.models import OuterRef, Subquery
from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HugoSession, HugoMessage, LearnerThemeMemory, Trace, TutorPrompt, TraceCriterionAssessment
from .renderers import ServerSentEventRenderer
from .serializers import (
    HugoSessionLearnerPatchSerializer,
    HugoSessionSerializer,
    SessionClassifierConfigSerializer,
)
from .llm_client import complete_with_provider, stream_with_provider
from .domain.conversation_profile import (
    ConversationPosture,
    ConversationProgress as ContractConversationProgress,
    SessionMaturityLevel,
    deserialize_conversation_progress,
)
from .domain.schemas import normalize_session_phase
from .domain.posture_transitions import can_transition
from .services.evaluation_blocking_reasons import can_request_evaluation
from .services.evaluation_service import (
    build_evaluation_preview,
    generate_evaluation_payload,
    get_or_create_policy,
    resolve_evaluation_readiness,
    save_evaluation_record,
)
from .services.memory_consolidator import consolidate_session
from .services.quality_tracker import record_session_signal
from .services.session_observability import increment_session_analytics_counter
from .services.evaluation_trace_pivot import enrich_trace_payload_with_pivot
from .services.hugo_orchestrator import build_hugo_turn
from .services.session_memory import build_session_memory
from .services.phase_decider import PHASE_CLASSIFIER_PRESETS
from .services.p0_classifier import P0_CLASSIFIER_PRESETS
from .services.synthesis_service import generate_synthesis
from .services.tutor_prompt_snapshot import build_tutor_prompt_snapshot
from .services.tracing import build_request_trace, build_response_trace, persist_rag_citations
from .services.ui_state_builder import build_contract_ui_state, resolve_learner_display_profile_for_session
from apps.referentials.models import ReferentialCriterion
from django.conf import settings

logger = logging.getLogger(__name__)
SESSION_PHASE_REFLECTION = {"deepening", "potential_closure"}
SESSION_PHASE_VALUES = {choice for choice, _ in HugoSession.SessionPhase.choices}
INDEXED_LINE_RE = re.compile(r"^\s*(\d{1,2})\s*[\.\)\:\-]?\s*(.+?)\s*$")
NEGATIVE_ANSWER_RE = re.compile(r"\b(non|pas\b|jamais|aucun|aucune|je ne sais)\b", flags=re.IGNORECASE)


def _one_question_guardrail(text: str) -> str:
    """Ensure at most one question; take first sentence if multiple."""
    text = (text or "").strip()
    if not text:
        return text
    parts = re.split(r"[.?!\n]+", text, maxsplit=1)
    first = (parts[0] + ".").strip() if parts else text
    if len(first) > 500:
        first = first[:497] + "..."
    return first


def _truncate_numbered_questions(text: str, max_questions: int) -> str:
    """
    For MULTI_QUESTION_NUMBERED prompts:
    keep only the first `max_questions` lines that look like numbered questions.
    """
    text = (text or "").rstrip()
    if not text or max_questions <= 0:
        return text

    lines = text.splitlines()
    kept: list[str] = []
    count = 0
    pattern = re.compile(r"^\s*\d+[.)]\s")  # e.g. '1. ' or '2) '

    for line in lines:
        if pattern.match(line):
            normalized_line = _normalize_numbered_line(line.rstrip())
            kept.append(normalized_line)
            count += 1
            if count >= max_questions:
                break

    # If nothing matched, return the original text
    return "\n".join(kept) if kept else text


def _extract_questions(text: str, max_questions: int) -> list[str]:
    if max_questions <= 0:
        return []
    clean = (text or "").strip()
    if not clean:
        return []
    questions = re.findall(r"[^?!\n]*\?+", clean)
    normalized: list[str] = []
    for q in questions:
        sq = " ".join(q.split()).strip()
        sq = _strip_index_prefix(sq)
        if sq and sq[-1] != "?":
            sq += "?"
        if sq:
            normalized.append(sq)
    return normalized[:max_questions]


def _strip_index_prefix(text: str) -> str:
    current = (text or "").strip()
    while True:
        updated = re.sub(r"^\s*\d+\s*[\.\)\:\-]\s*", "", current).strip()
        if updated == current:
            break
        current = updated
    return current


def _normalize_numbered_line(line: str) -> str:
    match = re.match(r"^\s*(\d+)\s*[\.\)]\s*(.*)$", (line or "").strip())
    if not match:
        return line
    idx = match.group(1)
    content = _strip_index_prefix(match.group(2))
    return f"{idx}. {content}".strip()


def _parse_indexed_lines(text: str, keep_questions_only: bool = False) -> dict[int, str]:
    entries: dict[int, str] = {}
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = INDEXED_LINE_RE.match(line)
        if not match:
            continue
        idx = int(match.group(1))
        payload = _strip_index_prefix(match.group(2))
        if not payload:
            continue
        if keep_questions_only and "?" not in payload:
            continue
        entries[idx] = payload
    return entries


def _build_indexed_alignment_content(
    learner_content: str,
    previous_assistant_content: str,
    max_pairs: int = 3,
) -> tuple[str, dict]:
    questions = _parse_indexed_lines(previous_assistant_content, keep_questions_only=True)
    answers = _parse_indexed_lines(learner_content, keep_questions_only=False)
    if not questions or not answers:
        return learner_content, {"applied": False, "pairs_count": 0}

    aligned_pairs: list[tuple[int, str, str]] = []
    for idx in sorted(answers.keys()):
        question = questions.get(idx)
        if not question:
            continue
        aligned_pairs.append((idx, question, answers[idx]))
        if len(aligned_pairs) >= max_pairs:
            break

    if not aligned_pairs:
        return learner_content, {"applied": False, "pairs_count": 0}

    lines = [
        "Reponse apprenant (verbatim):",
        learner_content.strip(),
        "",
        "Alignement Q/R du tour precedent :",
    ]
    for idx, question, answer in aligned_pairs:
        lines.append(f"Q{idx}: {question}")
        lines.append(f"R{idx}: {answer}")
    lines.append("")
    lines.append(
        "Consigne: Traite les lignes Rn comme reponse a Qn. "
        "Ne repose pas une question deja couverte sauf ambiguite explicite."
    )
    return "\n".join(lines).strip(), {"applied": True, "pairs_count": len(aligned_pairs)}


def _get_or_create_runtime_trace(session: HugoSession, organisation_id) -> Trace:
    trace = (
        Trace.objects.filter(
            organisation_id=organisation_id,
            session=session,
            validated_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if trace:
        return trace
    payload = {
        "session_id": str(session.id),
        "learner_id": str(session.learner_id),
        "messages_count": session.messages.count(),
        "evaluation_criteria": [],
        "evaluation_modalities": [],
        "expected_evidence": [],
    }
    return Trace.objects.create(
        organisation_id=organisation_id,
        session=session,
        payload_structured=payload,
    )


def _infer_criterion_status(learner_content: str) -> str:
    text = str(learner_content or "").strip()
    if not text:
        return TraceCriterionAssessment.CoverageStatus.NOT_SEEN
    if NEGATIVE_ANSWER_RE.search(text):
        return TraceCriterionAssessment.CoverageStatus.PARTIAL
    return TraceCriterionAssessment.CoverageStatus.COVERED


def _short_non_question_line(text: str) -> str:
    for raw_line in (text or "").splitlines():
        line = " ".join(raw_line.split()).strip()
        if line and "?" not in line:
            if len(line) > 220:
                return line[:217].rstrip() + "..."
            return line
    return ""


def _shorten_safe_question(question: str) -> str:
    clean = " ".join((question or "").split()).strip()
    if not clean:
        return clean
    if len(clean) <= 140:
        return clean
    for separator in [",", ";", " parce que ", " afin de ", " pour que "]:
        if separator in clean:
            clean = clean.split(separator)[0].strip()
            break
    if len(clean) > 140:
        clean = clean[:137].rstrip() + "..."
    if not clean.endswith("?"):
        clean = clean.rstrip(".") + " ?"
    return clean


def _build_assistant_display_variants(short_text: str, long_text: str) -> dict:
    short_value = str(short_text or "").strip()
    long_value = str(long_text or "").strip()
    variants = {
        "short": short_value,
        "long": long_value or short_value,
        "default_variant": "short",
    }
    available = [key for key in ["short", "long"] if variants.get(key)]
    if variants["short"] == variants["long"]:
        available = ["short"]
    variants["available_variants"] = available
    return variants


META_LEAK_PATTERNS = [
    r"rebondir sur le dernier message",
    r"j['’]aurais besoin de conna[iî]tre ce message",
    r"pourriez[- ]vous me le communiquer",
    r"tu [ée]changes avec un apprenant",
    r"system prompt",
    r"prompt interne",
    r"\binstruction\b",
]


def _decision_forces_no_question(
    max_questions: int,
    question_style: Optional[str],
    response_constraints: Optional[list[str]],
) -> bool:
    constraints = set(response_constraints or [])
    return max_questions <= 0 or question_style == "no_question" or "no_question_final" in constraints


def _decision_forces_single_question(
    question_style: Optional[str],
    response_constraints: Optional[list[str]],
) -> bool:
    constraints = set(response_constraints or [])
    return (
        question_style == "single_safe"
        or "single_question_only" in constraints
        or "no_question_stacking" in constraints
    )


def _derive_output_mode(
    configured_mode: Optional[str],
    session_phase: Optional[str],
    max_questions: int = 1,
    question_style: Optional[str] = None,
    response_constraints: Optional[list[str]] = None,
) -> str:
    if _decision_forces_no_question(max_questions, question_style, response_constraints):
        return TutorPrompt.OutputFormatMode.REFLECTION_BLOCK
    if _decision_forces_single_question(
        question_style,
        response_constraints,
    ):
        return TutorPrompt.OutputFormatMode.SINGLE_QUESTION
    if configured_mode == TutorPrompt.OutputFormatMode.REFLECTION_BLOCK:
        return TutorPrompt.OutputFormatMode.REFLECTION_BLOCK
    if configured_mode == TutorPrompt.OutputFormatMode.SINGLE_QUESTION:
        return TutorPrompt.OutputFormatMode.SINGLE_QUESTION
    if normalize_session_phase(session_phase) in SESSION_PHASE_REFLECTION:
        return TutorPrompt.OutputFormatMode.REFLECTION_BLOCK
    return TutorPrompt.OutputFormatMode.MULTI_QUESTION_NUMBERED


def _apply_output_guardrails(
    text: str,
    output_mode: str,
    max_questions: int,
    question_style: Optional[str] = None,
    response_constraints: Optional[list[str]] = None,
) -> str:
    if _decision_forces_no_question(max_questions, question_style, response_constraints):
        summary_line = _short_non_question_line(text)
        if summary_line:
            return summary_line
        stripped = " ".join((text or "").split()).strip()
        stripped = re.sub(r"[^.?!]*\?+", "", stripped).strip()
        if stripped:
            return stripped[:220].rstrip()
        return ""
    max_questions = max(1, min(max_questions, 3))
    if output_mode == TutorPrompt.OutputFormatMode.SINGLE_QUESTION or _decision_forces_single_question(
        question_style,
        response_constraints,
    ):
        questions = _extract_questions(text, 1)
        if questions:
            return _shorten_safe_question(questions[0]) if question_style == "single_safe" else questions[0]
        single = _one_question_guardrail(text)
        return _shorten_safe_question(single) if question_style == "single_safe" else single
    if output_mode == TutorPrompt.OutputFormatMode.REFLECTION_BLOCK:
        summary_line = _short_non_question_line(text)
        questions = _extract_questions(text, min(max_questions, 2))
        if summary_line and questions:
            return f"{summary_line}\n" + "\n".join(
                f"{idx + 1}. {q}" for idx, q in enumerate(questions)
            )
        if questions:
            return "\n".join(f"{idx + 1}. {q}" for idx, q in enumerate(questions))
        if summary_line:
            return summary_line
        return _one_question_guardrail(text)

    numbered = _truncate_numbered_questions(text, max_questions)
    if numbered != (text or "").rstrip():
        return numbered
    questions = _extract_questions(text, max_questions)
    if questions:
        return "\n".join(f"{idx + 1}. {q}" for idx, q in enumerate(questions))
    return _one_question_guardrail(text)


def _contains_meta_leak(text: str) -> bool:
    clean = str(text or "").strip()
    if not clean:
        return False
    return any(re.search(pattern, clean, flags=re.IGNORECASE) for pattern in META_LEAK_PATTERNS)


def _safe_assistant_fallback(
    *,
    turn_state: dict,
    conversation_decision: dict,
) -> str:
    if (
        str(turn_state.get("closure_signal") or "") == "explicit"
        or bool(conversation_decision.get("should_close"))
        or int(conversation_decision.get("number_of_questions") or 0) == 0
    ):
        return "D'accord, on peut s'arrêter ici."
    if str(turn_state.get("learner_help_request") or "") == "explicit":
        return "Je t'aide brievement: pars du dernier fait concret que tu as observe et verifie ce qui a pu provoquer l'ecart."
    if str(turn_state.get("repetition_signal") or "") in {"implicit", "explicit"}:
        return "Tu as raison, on ne va pas tourner en rond. Restons sur l'essentiel."
    return "Continuons a partir de ce que tu as deja decrit."


def _apply_meta_response_guardrail(
    *,
    reply: str,
    turn_state: dict,
    conversation_decision: dict,
) -> str:
    clean = str(reply or "").strip()
    if clean and not _contains_meta_leak(clean):
        return clean
    return _safe_assistant_fallback(
        turn_state=turn_state,
        conversation_decision=conversation_decision,
    )


def _normalize_phase(value: Optional[str]) -> Optional[str]:
    phase = normalize_session_phase(value, default="")
    return phase if phase in SESSION_PHASE_VALUES else None


def _session_queryset_for_learner(user):
    first_learner_message_subquery = (
        HugoMessage.objects.filter(
            session_id=OuterRef("pk"),
            role=HugoMessage.Role.LEARNER,
        )
        .order_by("created_at")
        .values("content")[:1]
    )
    return HugoSession.objects.filter(
        organisation_id=user.organisation_id,
        learner=user,
    ).annotate(first_learner_message_text=Subquery(first_learner_message_subquery))


class SessionListCreate(generics.ListCreateAPIView):
    """POST/GET /hugo/sessions — learner creates or lists own sessions."""
    serializer_class = HugoSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = _session_queryset_for_learner(self.request.user)
        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(messages__content__icontains=q).distinct()
        fav = (self.request.query_params.get("favorites_only") or "").strip().lower()
        if fav in ("1", "true", "yes"):
            qs = qs.filter(is_favorite=True)
        raw_after = (self.request.query_params.get("created_after") or "").strip()
        raw_before = (self.request.query_params.get("created_before") or "").strip()
        d_after = parse_date(raw_after) if raw_after else None
        d_before = parse_date(raw_before) if raw_before else None
        if d_after and d_before and d_after > d_before:
            d_after, d_before = d_before, d_after
        if d_after:
            qs = qs.filter(created_at__date__gte=d_after)
        if d_before:
            qs = qs.filter(created_at__date__lte=d_before)
        ordering = (self.request.query_params.get("ordering") or "-created_at").strip()
        if ordering == "created_at":
            qs = qs.order_by("created_at")
        else:
            qs = qs.order_by("-created_at")
        return qs

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=tenant_organisation_id(self.request),
            learner=self.request.user,
        )


class SessionDetail(generics.RetrieveUpdateAPIView):
    """GET/PATCH /hugo/sessions/{id} — learner reads or updates session (e.g. favorite)."""
    serializer_class = HugoSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "session_id"

    def get_queryset(self):
        return _session_queryset_for_learner(self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        patch_serializer = HugoSessionLearnerPatchSerializer(
            instance,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        patch_serializer.is_valid(raise_exception=True)
        self.perform_update(patch_serializer)
        instance.refresh_from_db()
        return Response(
            HugoSessionSerializer(instance, context=self.get_serializer_context()).data
        )


class SessionPhaseOverrideView(APIView):
    """PATCH /hugo/sessions/{session_id}/phase — set or clear manual phase override."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, session_id):
        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
            learner=request.user,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        raw_phase = request.data.get("manual_phase_override", None)
        if raw_phase in ("", None):
            session.manual_phase_override = None
            session.save(update_fields=["manual_phase_override", "updated_at"])
            return Response(
                {
                    "session_id": str(session.id),
                    "current_phase": session.current_phase,
                    "manual_phase_override": None,
                }
            )

        phase = _normalize_phase(str(raw_phase))
        if not phase:
            return Response(
                {
                    "detail": "manual_phase_override invalide.",
                    "allowed_values": sorted(SESSION_PHASE_VALUES),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.manual_phase_override = phase
        session.save(update_fields=["manual_phase_override", "updated_at"])
        return Response(
            {
                "session_id": str(session.id),
                "current_phase": session.current_phase,
                "manual_phase_override": session.manual_phase_override,
            }
        )


class SessionClassifierConfigView(APIView):
    """PATCH /hugo/sessions/{session_id}/classifier-config — set or clear runtime overrides."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, session_id):
        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
            learner=request.user,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SessionClassifierConfigSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        if not payload:
            return Response(
                {
                    "session_id": str(session.id),
                    "phase_classifier_enabled": session.phase_classifier_enabled,
                    "phase_classifier_max_tokens": session.phase_classifier_max_tokens,
                    "phase_classifier_min_confidence": session.phase_classifier_min_confidence,
                    "phase_classifier_max_input_chars": session.phase_classifier_max_input_chars,
                    "p0_classifier_enabled": session.p0_classifier_enabled,
                    "p0_classifier_max_tokens": session.p0_classifier_max_tokens,
                    "p0_classifier_min_confidence": session.p0_classifier_min_confidence,
                    "p0_classifier_max_input_chars": session.p0_classifier_max_input_chars,
                    "presets_reference": PHASE_CLASSIFIER_PRESETS,
                    "p0_presets_reference": P0_CLASSIFIER_PRESETS,
                }
            )

        for field, value in payload.items():
            setattr(session, field, value)
        update_fields = list(payload.keys()) + ["updated_at"]
        session.save(update_fields=update_fields)

        return Response(
            {
                "session_id": str(session.id),
                "phase_classifier_enabled": session.phase_classifier_enabled,
                "phase_classifier_max_tokens": session.phase_classifier_max_tokens,
                "phase_classifier_min_confidence": session.phase_classifier_min_confidence,
                "phase_classifier_max_input_chars": session.phase_classifier_max_input_chars,
                "p0_classifier_enabled": session.p0_classifier_enabled,
                "p0_classifier_max_tokens": session.p0_classifier_max_tokens,
                "p0_classifier_min_confidence": session.p0_classifier_min_confidence,
                "p0_classifier_max_input_chars": session.p0_classifier_max_input_chars,
                "presets_reference": PHASE_CLASSIFIER_PRESETS,
                "p0_presets_reference": P0_CLASSIFIER_PRESETS,
            }
        )


def _resolve_llm_provider(session: HugoSession) -> str:
    group = session.group
    if group and group.llm_backend:
        return group.llm_backend.lower()
    return getattr(settings, "LLM_PROVIDER_DEFAULT", "ollama").lower()


def _get_message_session(request, session_id) -> Optional[HugoSession]:
    return HugoSession.objects.select_related("group", "organisation").filter(
        id=session_id,
        organisation_id=tenant_organisation_id(request),
        learner=request.user,
    ).first()


def _get_contract_progress(session: HugoSession):
    raw = getattr(session, "conversation_progress", None)
    progress = deserialize_conversation_progress(raw if isinstance(raw, dict) else None)
    if progress is not None:
        return progress
    posture_value = getattr(session, "posture", None) or getattr(session, "conversation_profile_override", None) or ConversationPosture.REFLECTIVE_AFEST.value
    try:
        posture = ConversationPosture(str(posture_value))
    except ValueError:
        posture = ConversationPosture.REFLECTIVE_AFEST
    return ContractConversationProgress(session_id=str(session.id), posture=posture)


def _normalize_gamification_profile(value: str) -> str:
    normalized = str(value or "B").strip().upper()
    return normalized if normalized in {"A", "B", "C"} else "B"


def _resolve_learner_display_profile(request, session=None) -> str:
    return resolve_learner_display_profile_for_session(request=request, session=session)


def _post_conversation_hooks(session: HugoSession, progress: Optional[ContractConversationProgress] = None) -> None:
    contract_progress = progress or _get_contract_progress(session)
    consolidate_session(session, contract_progress)
    turn_count = session.messages.filter(role=HugoMessage.Role.LEARNER).count()
    record_session_signal(session, contract_progress, turn_count=turn_count)


def _validate_message_request(request) -> tuple[Optional[str], Optional[str], Optional[Response]]:
    content = (request.data.get("content") or "").strip()
    if not content:
        return None, None, Response({"detail": "content required."}, status=status.HTTP_400_BAD_REQUEST)

    requested_phase = _normalize_phase(request.data.get("session_phase"))
    if request.data.get("session_phase") not in (None, "") and not requested_phase:
        return None, None, Response(
            {
                "detail": "session_phase invalide.",
                "allowed_values": sorted(SESSION_PHASE_VALUES),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return content, requested_phase, None


class SessionProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(_get_contract_progress(session).to_dict())


class SessionUiStateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        profile = str(request.query_params.get("gamification_profile", "B") or "B").strip().upper()
        ui_state = build_contract_ui_state(
            session=session,
            progress=_get_contract_progress(session),
            gamification_profile=profile if profile in {"A", "B", "C"} else "B",
            learner_display_profile=_resolve_learner_display_profile(request, session),
        )
        return Response(ui_state.to_dict())


class SessionSetPostureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        requested = str(request.data.get("posture") or "").strip().lower()
        try:
            next_posture = ConversationPosture(requested)
        except ValueError:
            return Response({"detail": "Invalid posture."}, status=status.HTTP_400_BAD_REQUEST)
        progress = _get_contract_progress(session)
        current_value = getattr(session, "posture", "") or getattr(session, "conversation_profile_override", "") or progress.posture.value
        try:
            current_posture = ConversationPosture(current_value)
        except ValueError:
            current_posture = ConversationPosture.REFLECTIVE_AFEST
        allowed, warning = can_transition(current_posture, next_posture, progress.overall_maturity)
        if not allowed:
            return Response({"detail": "transition_not_allowed"}, status=status.HTTP_400_BAD_REQUEST)
        analytics_state = dict(getattr(session, "analytics_state", {}) or {})
        if current_posture != next_posture:
            analytics_state["posture_switch_count"] = int(analytics_state.get("posture_switch_count", 0) or 0) + 1
        session.analytics_state = analytics_state
        session.posture = next_posture.value
        session.conversation_profile_override = next_posture.value
        update_fields = ["posture", "conversation_profile_override", "analytics_state", "updated_at"]
        raw_progress = getattr(session, "conversation_progress", None)
        if isinstance(raw_progress, dict):
            session.conversation_progress = {**raw_progress, "posture": next_posture.value}
            update_fields.append("conversation_progress")
        session.save(update_fields=update_fields)
        return Response({"posture": session.posture, "warning": warning})


class SessionRequestSynthesisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        progress = _get_contract_progress(session)
        if not progress.synthesis_eligible:
            increment_session_analytics_counter(session, "cta_synthesis_blocked_count")
            return Response(
                {"error": "synthesis_not_eligible", "reason_codes": progress.reason_codes},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = _normalize_gamification_profile(
            request.data.get("gamification_profile")
            or request.query_params.get("gamification_profile")
            or "B"
        )
        display_profile = _resolve_learner_display_profile(request, session)
        synthesis = generate_synthesis(session, progress)
        analytics_state = dict(getattr(session, "analytics_state", {}) or {})
        analytics_state["synthesis_requested"] = True
        analytics_state["generated_artifacts"] = {
            **dict(analytics_state.get("generated_artifacts", {}) or {}),
            "synthesis": synthesis,
        }
        session.analytics_state = analytics_state
        session.save(update_fields=["analytics_state", "updated_at"])
        return Response(
            {
                "status": "synthesis_ready",
                "synthesis": synthesis,
                "ui_state": build_contract_ui_state(
                    session=session,
                    progress=progress,
                    gamification_profile=profile,
                    learner_display_profile=display_profile,
                ).to_dict(),
            }
        )


class SessionEvaluationReadinessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        progress = _get_contract_progress(session)
        return Response(resolve_evaluation_readiness(progress))


class SessionRequestEvaluationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        progress = _get_contract_progress(session)
        policy = get_or_create_policy(session.organisation, session.group)
        allowed, blocking_reasons = can_request_evaluation(
            session,
            progress,
            allow_early_trigger=bool(policy.allow_early_trigger),
        )
        if not allowed:
            increment_session_analytics_counter(session, "cta_evaluation_blocked_count")
            return Response(
                {
                    "error": "evaluation_not_eligible",
                    "blocking_reasons": blocking_reasons,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = _normalize_gamification_profile(
            request.data.get("gamification_profile")
            or request.query_params.get("gamification_profile")
            or "B"
        )
        display_profile = _resolve_learner_display_profile(request, session)
        evaluation_payload = generate_evaluation_payload(session, progress)
        record = save_evaluation_record(session, progress, evaluation_payload)
        evaluation = build_evaluation_preview(record, evaluation_payload)
        analytics_state = dict(getattr(session, "analytics_state", {}) or {})
        analytics_state["evaluation_requested"] = True
        analytics_state["generated_artifacts"] = {
            **dict(analytics_state.get("generated_artifacts", {}) or {}),
            "evaluation": evaluation,
        }
        session.analytics_state = analytics_state
        session.evaluation_in_progress = False
        session.save(update_fields=["analytics_state", "evaluation_in_progress", "updated_at"])
        return Response(
            {
                "status": "evaluation_ready",
                "evaluation": evaluation,
                "evaluation_record_id": str(record.id),
                "trigger_state": evaluation_payload["trigger_state"],
                "warning": evaluation_payload.get("warning"),
                "first_message": evaluation_payload.get("first_message"),
                "ui_state": build_contract_ui_state(
                    session=session,
                    progress=progress,
                    gamification_profile=profile,
                    learner_display_profile=display_profile,
                ).to_dict(),
            }
        )


class SessionFinalizeEvaluationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        progress = _get_contract_progress(session)
        payload = request.data.get("evaluation_output", {}) if isinstance(request.data, dict) else {}
        if not isinstance(payload, dict) or not payload:
            return Response({"error": "evaluation_output_required"}, status=status.HTTP_400_BAD_REQUEST)
        record = save_evaluation_record(session, progress, payload)
        policy = get_or_create_policy(session.organisation, session.group)
        session.evaluation_in_progress = False
        session.save(update_fields=["evaluation_in_progress", "updated_at"])
        return Response(
            {
                "evaluation_record_id": str(record.id),
                "overall_status": record.overall_status,
                "shared_with_tutor": record.shared_with_tutor,
                "tutor_validation_required": bool(policy.tutor_validation_required),
                "items_count": len(record.items or []),
                "evaluation_profile_used": record.evaluation_profile_used,
            }
        )


def _serialize_theme_memory(record: LearnerThemeMemory) -> dict:
    return {
        "theme_key": record.theme_key,
        "stabilised": record.stabilised_points,
        "open_loops": record.open_loops,
        "difficulties": record.persistent_difficulties,
        "status": record.knowledge_status,
        "last_session": str(record.last_conversation_id) if record.last_conversation_id else "",
        "updated_at": record.updated_at.isoformat(),
    }


class SessionMemorySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        session_memory_summary = build_session_memory(session)
        session_memory = (
            session_memory_summary.contract.to_dict()
            if session_memory_summary.contract is not None
            else {}
        )
        records = LearnerThemeMemory.objects.filter(
            organisation_id=tenant_organisation_id(request),
            learner_id=session.learner_id,
        ).order_by("-updated_at")[:10]
        return Response(
            {
                "session_memory": session_memory,
                "theme_memories": [_serialize_theme_memory(record) for record in records],
            }
        )


def _apply_focus_competence_trace(*, organisation_id, session, enriched_content: str, teaching_plan) -> tuple[str, str, list[str]]:
    focus_competence = getattr(teaching_plan, "focus_competence", {}) or {}
    focus_criterion_id = str(focus_competence.get("criterion_id") or "").strip()
    focus_criterion_code = str(focus_competence.get("criterion_code") or "").strip()
    focus_criterion_label = str(focus_competence.get("criterion_label") or "").strip()
    covered_criteria_codes = list(focus_competence.get("covered_criteria_codes") or [])

    if focus_criterion_id:
        criterion = ReferentialCriterion.objects.filter(
            id=focus_criterion_id,
            organisation_id=organisation_id,
        ).first()
        if criterion:
            runtime_trace = _get_or_create_runtime_trace(session, organisation_id)
            status_value = _infer_criterion_status(enriched_content)
            TraceCriterionAssessment.objects.update_or_create(
                organisation_id=organisation_id,
                trace=runtime_trace,
                criterion=criterion,
                defaults={
                    "status": status_value,
                    "confidence": 0.7 if status_value == TraceCriterionAssessment.CoverageStatus.COVERED else 0.4,
                    "notes": "auto_from_dialogue",
                },
            )

    return focus_criterion_code, focus_criterion_label, covered_criteria_codes


def _build_llm_messages(session: HugoSession, system_prompt: str, user_prompt: str) -> list[dict]:
    history_qs = session.messages.order_by("created_at")
    conversation_messages: list[dict] = []
    for message in history_qs:
        role = "assistant" if message.role == HugoMessage.Role.ASSISTANT else "user"
        conversation_messages.append({"role": role, "content": message.content})

    llm_messages = [{"role": "system", "content": system_prompt}] + conversation_messages
    if llm_messages and llm_messages[-1].get("role") == "user":
        llm_messages[-1]["content"] = user_prompt
    else:
        llm_messages.append({"role": "user", "content": user_prompt})
    return llm_messages


def _build_message_turn_runtime(request, session: HugoSession, content: str, requested_phase: Optional[str]) -> dict:
    previous_assistant_msg = (
        session.messages.filter(role=HugoMessage.Role.ASSISTANT)
        .order_by("-created_at")
        .first()
    )
    enriched_content, alignment_meta = _build_indexed_alignment_content(
        learner_content=content,
        previous_assistant_content=getattr(previous_assistant_msg, "content", ""),
    )
    learner_msg = HugoMessage.objects.create(
        organisation_id=tenant_organisation_id(request),
        session=session,
        role=HugoMessage.Role.LEARNER,
        content=content,
    )

    user_input = {"content": enriched_content}
    if requested_phase:
        user_input["session_phase"] = requested_phase

    turn = build_hugo_turn(session, user_input)
    system_prompt = turn.system_prompt
    user_prompt = turn.user_prompt
    resolved_tutor_prompt = turn.tutor_prompt
    teaching_plan = turn.teaching_plan

    focus_criterion_code, focus_criterion_label, covered_criteria_codes = _apply_focus_competence_trace(
        organisation_id=tenant_organisation_id(request),
        session=session,
        enriched_content=enriched_content,
        teaching_plan=teaching_plan,
    )

    provider = _resolve_llm_provider(session)
    max_tokens = getattr(resolved_tutor_prompt, "max_tokens", None) or 150
    configured_mode = getattr(
        resolved_tutor_prompt,
        "output_format_mode",
        TutorPrompt.OutputFormatMode.SINGLE_QUESTION,
    )
    configured_max_questions = getattr(
        resolved_tutor_prompt,
        "max_questions_per_turn",
        None,
    ) or 1
    planned_max_questions = getattr(teaching_plan, "max_questions_this_turn", None)
    if planned_max_questions is None:
        planned_max_questions = configured_max_questions
    effective_max_questions_this_turn = max(0, min(configured_max_questions, planned_max_questions))
    session_phase = turn.effective_phase
    next_session_phase = turn.next_phase
    phase_decision = turn.phase_decision or {}
    p0_classifier = turn.p0_classifier or {}
    conversation_decision = turn.conversation_decision.to_dict() if turn.conversation_decision else {}
    turn_state = turn.turn_state.to_dict() if turn.turn_state else {}
    rag_selections = list(turn.rag_selections or [])
    question_style = str(conversation_decision.get("question_style") or "")
    response_constraints = list(conversation_decision.get("response_constraints") or [])
    output_mode = _derive_output_mode(
        configured_mode,
        session_phase,
        effective_max_questions_this_turn,
        question_style=question_style,
        response_constraints=response_constraints,
    )

    if next_session_phase and next_session_phase in SESSION_PHASE_VALUES and session.current_phase != next_session_phase:
        session.current_phase = next_session_phase
        session.save(update_fields=["current_phase", "updated_at"])

    llm_messages = _build_llm_messages(session, system_prompt, user_prompt)

    return {
        "request": request,
        "session": session,
        "content": content,
        "requested_phase": requested_phase,
        "alignment_meta": alignment_meta,
        "learner_msg": learner_msg,
        "turn": turn,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "resolved_tutor_prompt": resolved_tutor_prompt,
        "teaching_plan": teaching_plan,
        "provider": provider,
        "max_tokens": max_tokens,
        "configured_mode": configured_mode,
        "effective_max_questions_this_turn": effective_max_questions_this_turn,
        "session_phase": session_phase,
        "next_session_phase": next_session_phase,
        "phase_decision": phase_decision,
        "p0_classifier": p0_classifier,
        "conversation_decision": conversation_decision,
        "turn_state": turn_state,
        "conversation_profile": turn.conversation_profile,
        "conversation_progress": turn.conversation_progress.to_dict() if turn.conversation_progress else {},
        "session_memory": turn.session_memory.to_dict() if turn.session_memory else {},
        "ui_state": turn.ui_state.to_dict() if turn.ui_state else {},
        "rag_selections": rag_selections,
        "question_style": question_style,
        "response_constraints": response_constraints,
        "output_mode": output_mode,
        "focus_criterion_code": focus_criterion_code,
        "focus_criterion_label": focus_criterion_label,
        "covered_criteria_codes": covered_criteria_codes,
        "llm_messages": llm_messages,
    }


def _persist_learner_request_trace(runtime: dict, llm_meta: dict) -> None:
    learner_msg = runtime["learner_msg"]
    resolved_tutor_prompt = runtime["resolved_tutor_prompt"]
    learner_msg.llm_request_payload = build_request_trace(
        provider=runtime["provider"],
        llm_meta=llm_meta,
        system_prompt=runtime["system_prompt"],
        user_prompt=runtime["user_prompt"],
        max_tokens=runtime["max_tokens"],
        resolved_tutor_prompt_id=str(resolved_tutor_prompt.id) if resolved_tutor_prompt else None,
        tutor_prompt_snapshot=build_tutor_prompt_snapshot(resolved_tutor_prompt),
        configured_output_mode=runtime["configured_mode"],
        output_mode=runtime["output_mode"],
        effective_max_questions_this_turn=runtime["effective_max_questions_this_turn"],
        session_phase=runtime["session_phase"],
        next_session_phase=runtime["next_session_phase"],
        requested_phase=runtime["requested_phase"],
        manual_phase_override=runtime["session"].manual_phase_override,
        alignment_meta=runtime["alignment_meta"],
        phase_decision=runtime["phase_decision"],
        p0_classifier=runtime["p0_classifier"],
        turn_state=runtime["turn_state"],
        conversation_decision=runtime["conversation_decision"],
        conversation_profile=runtime["conversation_profile"],
        conversation_progress=runtime["conversation_progress"],
        ui_state=runtime["ui_state"],
        session_memory=runtime["session_memory"],
        focus_criterion_code=runtime["focus_criterion_code"],
        focus_criterion_label=runtime["focus_criterion_label"],
        covered_criteria_codes=runtime["covered_criteria_codes"],
        rag_selections=runtime["rag_selections"],
        prompt_sources=runtime["turn"].prompt_sources,
    )
    learner_msg.save(update_fields=["llm_request_payload"])


def _apply_reply_guardrails(runtime: dict, reply_before_guardrails: str) -> tuple[str, dict]:
    conversation_decision = runtime["conversation_decision"]
    turn_state = runtime["turn_state"]
    response_constraints = runtime["response_constraints"]
    question_style = runtime["question_style"]
    reply = reply_before_guardrails

    if str(conversation_decision.get("metadata", {}).get("contract_version") or "") == "1.7":
        from apps.hugo.domain.conversation_decision_v17 import ConversationDecisionV17
        from apps.hugo.services.output_guardrails_v17 import apply_output_guardrails_v17
        from apps.hugo.services.prompt_renderer_v17 import TutorPromptProfile

        decision_v17 = ConversationDecisionV17(
            primary_intent=str(conversation_decision.get("primary_intent") or ""),
            pedagogical_move=str(conversation_decision.get("pedagogical_move") or ""),
            response_mode=str(conversation_decision.get("metadata", {}).get("response_mode") or "reflect"),
            target_question_count=int(conversation_decision.get("metadata", {}).get("target_question_count") or runtime["effective_max_questions_this_turn"]),
            number_of_questions=int(conversation_decision.get("number_of_questions") or 0),
            question_style=question_style or "simple_open",
            question_bundling_allowed=int(conversation_decision.get("number_of_questions") or 0) > 1,
            micro_explanation_allowed=bool(conversation_decision.get("should_explain_briefly")),
            should_explain_briefly=bool(conversation_decision.get("should_explain_briefly")),
            should_recap=bool(conversation_decision.get("should_recap")),
            should_encourage=bool(conversation_decision.get("should_encourage")),
            should_reframe=bool(conversation_decision.get("should_reframe")),
            should_close=bool(conversation_decision.get("should_close")),
            should_acknowledge_repetition=str(turn_state.get("repetition_signal") or "") == "explicit",
            should_acknowledge_closure=str(turn_state.get("closure_signal") or "") == "explicit",
            blocked_question_topics=list(conversation_decision.get("metadata", {}).get("blocked_question_topics") or []),
            response_constraints=response_constraints,
            reason_codes=list(conversation_decision.get("reason_codes") or []),
            metadata=dict(conversation_decision.get("metadata") or {}),
            effective_max_questions_this_turn=runtime["effective_max_questions_this_turn"],
        )
        profile = TutorPromptProfile(
            session=runtime["session"],
            tutor_prompt=runtime["resolved_tutor_prompt"],
            teaching_plan=runtime["teaching_plan"],
            competence_brief=None,
            learner_message=runtime["content"],
            context=None,
            rag_chunks=[selection.prompt_snippet() for selection in runtime["rag_selections"]],
        )
        reply = apply_output_guardrails_v17(reply, decision_v17, profile)
    else:
        reply = _apply_output_guardrails(
            reply,
            runtime["output_mode"],
            runtime["effective_max_questions_this_turn"],
            question_style=question_style,
            response_constraints=response_constraints,
        )

    reply = _apply_meta_response_guardrail(
        reply=reply,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
    )
    if not reply:
        reply = _safe_assistant_fallback(
            turn_state=turn_state,
            conversation_decision=conversation_decision,
        )

    return reply, _build_assistant_display_variants(
        short_text=reply,
        long_text=reply_before_guardrails,
    )


def _persist_assistant_reply(runtime: dict, reply_before_guardrails: str, llm_meta: dict) -> HugoMessage:
    reply, assistant_display_variants = _apply_reply_guardrails(runtime, reply_before_guardrails)
    message = HugoMessage.objects.create(
        organisation_id=runtime["request"].user.organisation_id,
        session=runtime["session"],
        role=HugoMessage.Role.ASSISTANT,
        content=reply,
        assistant_display_variants=assistant_display_variants,
    )
    message.llm_response_payload = build_response_trace(
        provider=runtime["provider"],
        llm_meta=llm_meta,
        rag_selections=runtime["rag_selections"],
        assistant_text_before_guardrails=reply_before_guardrails,
        prompt_sources=runtime["turn"].prompt_sources,
    )
    message.save(update_fields=["llm_response_payload"])
    persist_rag_citations(
        organisation_id=runtime["request"].user.organisation_id,
        assistant_message=message,
        rag_selections=runtime["rag_selections"],
    )
    return message


def _compact_rag_citations(message: HugoMessage) -> list[dict]:
    return [
        {
            "document_id": str(citation.document_id),
            "document_title": str(getattr(citation.document, "title", "") or ""),
            "chunk_id": str(citation.chunk_id),
            "score": citation.score,
            "reason": str((citation.meta or {}).get("reason") or ""),
        }
        for citation in message.rag_citations.select_related("document").order_by("-created_at")[:3]
    ]


def _serialize_message_response(runtime: dict, message: HugoMessage) -> dict:
    return {
        "id": str(message.id),
        "role": message.role,
        "content": message.content,
        "assistant_display_variants": message.assistant_display_variants,
        "rag_citations": _compact_rag_citations(message),
        "created_at": message.created_at.isoformat(),
        "effective_phase": runtime["session_phase"],
        "next_phase": runtime["next_session_phase"],
        "current_phase": runtime["session"].current_phase,
        "manual_phase_override": runtime["session"].manual_phase_override,
        "conversation_profile": runtime["conversation_profile"],
        "conversation_progress": runtime["conversation_progress"],
        "session_memory": runtime["session_memory"],
        "ui_state": runtime["ui_state"],
        "phase_decision_source": runtime["phase_decision"].get("source", "fallback_rules"),
        "adapter_next_phase": runtime["phase_decision"].get("adapter_next_phase", ""),
        "phase_runtime_config_source": runtime["phase_decision"].get("runtime_config_source", {}),
        "phase_runtime_config": runtime["phase_decision"].get("runtime_config", {}),
        "turn_state": runtime["turn_state"],
        "conversation_decision": runtime["conversation_decision"],
        "focus_criterion_code": runtime["focus_criterion_code"],
        "focus_criterion_label": runtime["focus_criterion_label"],
    }


def _sse_event(event_name: str, payload: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _stream_phase_label(phase_value: str) -> str:
    normalized = str(phase_value or "").strip().lower()
    if normalized == "opening":
        return "Raconter"
    if normalized == "exploration":
        return "Comprendre"
    if normalized in {"conceptualization", "deepening"}:
        return "Retenir"
    if normalized in {"closure", "potential_closure"}:
        return "Transmettre"
    return "Raconter"


def _stream_status_payload(runtime: dict, code: str, label: str, message: str) -> dict:
    phase_value = runtime.get("session_phase") or runtime["session"].current_phase
    progress = runtime.get("conversation_progress") or {}
    return {
        "code": code,
        "label": label,
        "message": f"{message} Objectif actif : {progress.get('active_objective', runtime.get('conversation_profile', 'reflective_afest'))}.",
        "phase": phase_value,
        "phase_label": _stream_phase_label(phase_value),
        "conversation_profile": runtime.get("conversation_profile", "reflective_afest"),
    }

class MessageListCreate(APIView):
    """GET/POST /hugo/sessions/{session_id}/messages — list (learner only) or send message."""
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
            learner=request.user,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        messages = session.messages.order_by("created_at")
        return Response({
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "assistant_display_variants": (
                        m.assistant_display_variants if m.role == HugoMessage.Role.ASSISTANT else {}
                    ),
                    "rag_citations": _compact_rag_citations(m) if m.role == HugoMessage.Role.ASSISTANT else [],
                    "created_at": m.created_at.isoformat(),
                    "llm_request_payload": m.llm_request_payload if m.role == HugoMessage.Role.LEARNER else {},
                    "llm_response_payload": m.llm_response_payload if m.role == HugoMessage.Role.ASSISTANT else {},
                }
                for m in messages
            ]
        })

    def post(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        content, requested_phase, error_response = _validate_message_request(request)
        if error_response is not None:
            return error_response

        runtime = _build_message_turn_runtime(request, session, content, requested_phase)
        if runtime["provider"] == "ovh_ai":
            reply, llm_meta = complete_with_provider(
                prompt=runtime["user_prompt"],
                system=runtime["system_prompt"],
                max_tokens=runtime["max_tokens"],
                provider=runtime["provider"],
                tutor_prompt=runtime["resolved_tutor_prompt"],
                messages=runtime["llm_messages"],
            )
        else:
            reply, llm_meta = complete_with_provider(
                prompt=runtime["user_prompt"],
                system=runtime["system_prompt"],
                max_tokens=runtime["max_tokens"],
                provider=runtime["provider"],
                tutor_prompt=runtime["resolved_tutor_prompt"],
            )

        _persist_learner_request_trace(runtime, llm_meta)
        message = _persist_assistant_reply(runtime, reply, llm_meta)
        _post_conversation_hooks(session)
        return Response(_serialize_message_response(runtime, message))


class MessageStreamCreate(APIView):
    """POST /hugo/sessions/{session_id}/messages/stream — send message and stream assistant chunks."""
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, ServerSentEventRenderer]

    def post(self, request, session_id):
        session = _get_message_session(request, session_id)
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        content, requested_phase, error_response = _validate_message_request(request)
        if error_response is not None:
            return error_response

        runtime = _build_message_turn_runtime(request, session, content, requested_phase)
        stream_iter, llm_meta = stream_with_provider(
            prompt=runtime["user_prompt"],
            system=runtime["system_prompt"],
            max_tokens=runtime["max_tokens"],
            provider=runtime["provider"],
            tutor_prompt=runtime["resolved_tutor_prompt"],
            messages=runtime["llm_messages"],
        )
        _persist_learner_request_trace(runtime, llm_meta)

        def event_stream():
            accumulated_chunks: list[str] = []
            emitted_any_chunk = False
            try:
                yield _sse_event(
                    "status",
                    _stream_status_payload(
                        runtime,
                        code="analysis",
                        label="Analyse",
                        message="Hugo analyse ta réponse...",
                    ),
                )
                yield _sse_event(
                    "status",
                    _stream_status_payload(
                        runtime,
                        code="reflection",
                        label="Réflexion",
                        message="Hugo réfléchit...",
                    ),
                )
                for chunk in stream_iter:
                    if not chunk:
                        continue
                    if not emitted_any_chunk:
                        yield _sse_event(
                            "status",
                            _stream_status_payload(
                                runtime,
                                code="response",
                                label="Réponse",
                                message="Hugo est en train de répondre...",
                            ),
                        )
                    emitted_any_chunk = True
                    accumulated_chunks.append(chunk)
                    yield _sse_event("chunk", {"text": chunk})

                reply_before_guardrails = llm_meta.get("full_text", "".join(accumulated_chunks))
                if llm_meta.get("error") and not emitted_any_chunk:
                    yield _sse_event("error", {"detail": llm_meta.get("error")})

                message = _persist_assistant_reply(runtime, reply_before_guardrails, llm_meta)
                _post_conversation_hooks(runtime["session"])
                yield _sse_event("done", _serialize_message_response(runtime, message))
            except Exception as exc:
                logger.exception(
                    "hugo_message_stream_failed",
                    extra={"session_id": str(runtime["session"].id), "error": str(exc)},
                )
                llm_meta.setdefault("error", str(exc))
                reply_before_guardrails = llm_meta.get("full_text", "".join(accumulated_chunks))
                if not emitted_any_chunk:
                    yield _sse_event("error", {"detail": str(exc)})
                message = _persist_assistant_reply(runtime, reply_before_guardrails, llm_meta)
                _post_conversation_hooks(runtime["session"])
                yield _sse_event("done", _serialize_message_response(runtime, message))

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class GenerateTraceView(APIView):
    """POST /hugo/sessions/{session_id}/generate-trace — build trace_rich_v1 from session."""
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
            learner=request.user,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        payload = {
            "session_id": str(session.id),
            "learner_id": str(session.learner_id),
            "messages_count": session.messages.count(),
            "evaluation_criteria": [],
            "evaluation_modalities": [],
            "expected_evidence": [],
        }
        enriched_payload = enrich_trace_payload_with_pivot(session, payload)
        trace = Trace.objects.create(
            organisation_id=tenant_organisation_id(request),
            session=session,
            payload_structured=enriched_payload,
        )
        progress = deserialize_conversation_progress(
            session.conversation_progress if isinstance(session.conversation_progress, dict) else None
        )
        if progress is not None:
            _post_conversation_hooks(session, progress)
        return Response(
            {
                "id": str(trace.id),
                "payload_structured": trace.payload_structured,
                "evaluation_trace_pivot_v1": enriched_payload.get("evaluation_trace_pivot_v1"),
            },
            status=status.HTTP_201_CREATED,
        )


class ShareView(APIView):
    """POST /hugo/sessions/{session_id}/share — set share_summary, share_evidence, share_verbatim."""
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = HugoSession.objects.filter(
            id=session_id,
            organisation_id=tenant_organisation_id(request),
            learner=request.user,
        ).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        session.share_summary = request.data.get("share_summary", session.share_summary)
        session.share_evidence = request.data.get("share_evidence", session.share_evidence)
        session.share_verbatim = request.data.get("share_verbatim", session.share_verbatim)
        session.save()
        from apps.quality.views import log_audit
        log_audit(request, "session_share", "hugo_session", session.id)
        return Response({
            "share_summary": session.share_summary,
            "share_evidence": session.share_evidence,
            "share_verbatim": session.share_verbatim,
        })
