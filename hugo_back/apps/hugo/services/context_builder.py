"""
Context builder for Hugo AFEST questions.

Builds a compact, textual context for the LLM based on:
- group referential + items (criteria, expected evidence),
- overlays (example situations, coach questions, common mistakes),
- learner history (LearnerState, recent traces),
- class documents (ACTIVE group documents titles).

IMPORTANT: read-only; no schema / RLS changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from django.db.models import Prefetch, Q

from apps.hugo.models import (
    HugoSession,
    Trace,
    LearnerState,
    TutorPrompt,
    TraceCriterionAssessment,
)
from apps.hugo.domain.schemas import normalize_session_phase
from apps.library.models import GroupDocument, Document
from apps.referentials.models import (
    ReferentialConfig,
    ReferentialCriterion,
    ReferentialCompetencyTask,
    ReferentialItem,
    ReferentialItemOverlay,
)


@dataclass
class CriterionSummary:
    id: str
    code: str
    label: str
    order_index: int
    expected_evidence: List[str] = field(default_factory=list)
    question_seeds: List[str] = field(default_factory=list)
    coverage_status: str = "not_seen"


@dataclass
class ItemSummary:
    id: str
    code: str
    title: str
    block_code: str
    block_label: str
    evaluation_criteria: List[str]
    expected_evidence: List[str]
    criteria: List[CriterionSummary]
    covered_criteria_codes: List[str]
    coach_questions: List[str]
    common_mistakes: List[str]
    example_situations: List[str]
    example_evidence: List[str]
    linked_documents: List[str]
    tasks: List[dict] = field(default_factory=list)


@dataclass
class HugoContext:
    referential_name: Optional[str]
    referential_source_ref: Optional[str]
    items_to_focus: List[ItemSummary]
    items_already_covered: List[ItemSummary]
    learner_summary: Optional[str]
    recent_traces_info: List[str]
    class_documents: List[str]


def _build_criterion_coverage_map(session: HugoSession) -> dict[str, str]:
    statuses = {}
    assessments = (
        TraceCriterionAssessment.objects.filter(
            organisation_id=session.organisation_id,
            trace__session__learner_id=session.learner_id,
            trace__session__group_id=session.group_id,
        )
        .select_related("criterion")
        .order_by("criterion_id", "-updated_at")
    )
    for assessment in assessments:
        criterion_id = str(assessment.criterion_id)
        if criterion_id in statuses:
            continue
        statuses[criterion_id] = assessment.status
    return statuses


def _get_referential_items_for_group(session: HugoSession) -> tuple[Optional[str], Optional[str], List[ItemSummary]]:
    """
    Return referential metadata and a list of item summaries for the group.
    """
    if not session.group_id:
        return None, None, []

    org_id = session.organisation_id
    group_id = session.group_id

    config = (
        ReferentialConfig.objects.select_related("referential")
        .filter(
            organisation_id=org_id,
            group_id=group_id,
        )
        .first()
    )
    if not config:
        return None, None, []

    ref = config.referential
    # Load items with overlays in one go
    overlays_qs = ReferentialItemOverlay.objects.filter(
        organisation_id=org_id,
        group_id=group_id,
        enabled=True,
    )
    criteria_qs = ReferentialCriterion.objects.filter(
        organisation_id=org_id,
        is_active=True,
    ).order_by("order_index", "code")
    competency_tasks_qs = ReferentialCompetencyTask.objects.select_related("task__activity").order_by(
        "task__activity__order_index",
        "task__order_index",
        "task__code",
    )
    items = (
        ReferentialItem.objects.filter(
            organisation_id=org_id,
            referential=ref,
        )
        .prefetch_related(
            Prefetch("overlays", queryset=overlays_qs),
            Prefetch("criteria", queryset=criteria_qs),
            Prefetch("competency_tasks", queryset=competency_tasks_qs),
        )
        .order_by("code")
    )
    coverage_map = _build_criterion_coverage_map(session)

    summaries: List[ItemSummary] = []
    for it in items:
        overlay = next(iter(it.overlays.all()), None)
        criteria_items: List[CriterionSummary] = []
        covered_codes: List[str] = []
        for crit in it.criteria.all():
            expected_evidence = [
                e.get("label") if isinstance(e, dict) else str(e)
                for e in (crit.expected_evidence or [])
            ]
            question_seeds = [
                q.get("label") if isinstance(q, dict) else str(q)
                for q in (crit.question_seeds or [])
            ]
            coverage_status = coverage_map.get(str(crit.id), "not_seen")
            criteria_items.append(
                CriterionSummary(
                    id=str(crit.id),
                    code=crit.code,
                    label=crit.label,
                    order_index=crit.order_index,
                    expected_evidence=expected_evidence,
                    question_seeds=question_seeds,
                    coverage_status=coverage_status,
                )
            )
            if coverage_status == TraceCriterionAssessment.CoverageStatus.COVERED:
                covered_codes.append(crit.code)
        evaluation_criteria = [c.label for c in criteria_items]
        expected_evidence = [e.get("label") if isinstance(e, dict) else str(e) for e in (it.expected_evidence or [])]
        coach_questions = list((overlay.coach_questions if overlay else []) or [])
        common_mistakes = list((overlay.common_mistakes if overlay else []) or [])
        example_situations = list((overlay.example_situations if overlay else []) or [])
        example_evidence = [
            entry.get("label") if isinstance(entry, dict) else str(entry)
            for entry in ((overlay.example_evidence if overlay else []) or [])
        ]
        linked_documents = [
            entry.get("reason") if isinstance(entry, dict) else str(entry)
            for entry in ((overlay.linked_documents if overlay else []) or [])
        ]
        tasks = []
        for link in it.competency_tasks.all():
            task = getattr(link, "task", None)
            activity = getattr(task, "activity", None) if task else None
            if not task:
                continue
            tasks.append(
                {
                    "task_code": str(getattr(task, "code", "") or "").strip(),
                    "task_label": str(getattr(task, "label", "") or "").strip(),
                    "activity_code": str(getattr(activity, "code", "") or "").strip(),
                    "activity_label": str(getattr(activity, "label", "") or "").strip(),
                }
            )
        summaries.append(
            ItemSummary(
                id=str(it.id),
                code=it.code,
                title=it.title,
                block_code=str(it.block_code or "").strip(),
                block_label=str(it.block_label or "").strip(),
                evaluation_criteria=evaluation_criteria,
                expected_evidence=expected_evidence,
                criteria=criteria_items,
                covered_criteria_codes=covered_codes,
                coach_questions=coach_questions,
                common_mistakes=common_mistakes,
                example_situations=example_situations,
                example_evidence=example_evidence,
                linked_documents=linked_documents,
                tasks=tasks,
            )
        )
    return ref.name, ref.source_ref, summaries


def _partition_items_by_coverage(
    session: HugoSession,
    items: List[ItemSummary],
) -> tuple[List[ItemSummary], List[ItemSummary]]:
    """
    Split items into (already_covered, to_focus) based on existing traces for this learner/group.
    """
    if not items:
        return [], []

    already_covered: List[ItemSummary] = []
    to_focus: List[ItemSummary] = []
    for it in items:
        if it.criteria and all(c.coverage_status == TraceCriterionAssessment.CoverageStatus.COVERED for c in it.criteria):
            already_covered.append(it)
        else:
            to_focus.append(it)
    return already_covered, to_focus


def _build_recent_traces_info(session: HugoSession, limit: int = 3) -> List[str]:
    org_id = session.organisation_id
    learner_id = session.learner_id
    group_id = session.group_id
    qs = Trace.objects.filter(
        organisation_id=org_id,
        session__learner_id=learner_id,
    )
    if group_id:
        qs = qs.filter(session__group_id=group_id)
    qs = qs.order_by("-created_at")[:limit]

    infos: List[str] = []
    for t in qs:
        status = "validée" if t.validated_at else "en cours"
        infos.append(
            f"Trace {str(t.id)[:8]} ({t.created_at.date().isoformat()}), {status}"
        )
    return infos


def _build_class_documents(session: HugoSession, limit: int = 3) -> List[str]:
    if not session.group_id:
        return []
    org_id = session.organisation_id
    group_id = session.group_id
    docs = (
        GroupDocument.objects.select_related("document")
        .filter(
            organisation_id=org_id,
            group_id=group_id,
            status=GroupDocument.Status.ACTIVE,
        )
        .order_by("-created_at")[:limit]
    )
    return [d.document.title for d in docs]


def build_hugo_context(session: HugoSession) -> HugoContext:
    """
    Build a compact context object for the LLM based on the current session.
    """
    # Referential + overlays
    ref_name, ref_source, all_items = _get_referential_items_for_group(session)
    already_covered, to_focus = _partition_items_by_coverage(session, all_items)

    # Limit number of items sent to the LLM for brevity
    items_to_focus = to_focus[:3]
    items_already_covered = already_covered[:3]

    # LearnerState summary (if any)
    learner_state = (
        LearnerState.objects.filter(
            organisation_id=session.organisation_id,
            learner_id=session.learner_id,
        )
        .filter(Q(group_id=session.group_id) | Q(group_id__isnull=True))
        .order_by("-updated_at")
        .first()
    )
    learner_summary = learner_state.summary if learner_state and learner_state.summary else None

    recent_traces_info = _build_recent_traces_info(session)
    class_documents = _build_class_documents(session)

    return HugoContext(
        referential_name=ref_name,
        referential_source_ref=ref_source,
        items_to_focus=items_to_focus,
        items_already_covered=items_already_covered,
        learner_summary=learner_summary,
        recent_traces_info=recent_traces_info,
        class_documents=class_documents,
    )


def _resolve_tutor_prompt(session: HugoSession, posture: str | None = None) -> TutorPrompt | None:
    """
    Resolve the TutorPrompt to use for this session.

    Priority:
    - explicit session.tutor_prompt if set and active,
    - global learner profile slot for posture (if profile resolved),
    - default prompt on group (legacy default_tutor_prompt),
    - default TutorPrompt for organisation / AFEST_HUGO if any,
    - otherwise: None (caller may fall back to legacy behaviour).
    """
    if session.tutor_prompt and session.tutor_prompt.is_active:
        return session.tutor_prompt

    from apps.hugo.services.learner_profile_resolver import resolve_tutor_prompt_from_global_profile

    effective_posture = posture or getattr(session, "posture", None) or getattr(
        session, "conversation_profile_override", None
    )
    global_prompt = resolve_tutor_prompt_from_global_profile(session, effective_posture)
    if global_prompt is not None:
        return global_prompt

    group = getattr(session, "group", None)
    default_group_prompt = getattr(group, "default_tutor_prompt", None) if group else None
    if default_group_prompt and default_group_prompt.is_active:
        return default_group_prompt

    return (
        TutorPrompt.objects.filter(
            organisation=session.organisation,
            prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
            is_active=True,
            is_default=True,
        )
        .order_by("created_at")
        .first()
    )


def _build_afest_prompts_legacy(
    session: HugoSession,
    content: str,
    ctx: HugoContext,
    session_phase: str = "exploration",
    max_questions: int = 2,
) -> tuple[str, str]:
    """
    Legacy implementation of AFEST prompts, kept as fallback.
    """
    phase = normalize_session_phase(session_phase)
    max_questions = max(1, min(max_questions, 3))
    reflection_phase = phase in {"deepening", "potential_closure"}

    response_rules: list[str]
    if reflection_phase:
        response_rules = [
            "- Tu rédiges un bloc réflexif court : 1 constat concret puis 1 à 2 questions courtes.",
            "- Les questions doivent rester centrées sur un même foyer de réflexion.",
            "- Pas de cours magistral, pas de longues explications, pas de liste de conseils détaillés.",
        ]
    else:
        response_rules = [
            f"- Tu poses {max_questions if max_questions <= 2 else '2 à 3'} questions courtes au maximum.",
            "- Ta réponse doit être uniquement des questions, en français.",
            "- Les questions doivent être courtes, distinctes et centrées sur un même foyer de réflexion.",
            "- Pas de cours magistral, pas de longues explications, pas de liste de conseils détaillés.",
        ]

    system_parts: list[str] = [
        "Tu es Hugo, assistant AFEST pour un apprenant.",
        "Ton rôle est de l'aider à analyser ses situations de travail et à progresser vers les compétences visées.",
        "Règles de réponse :",
        *response_rules,
    ]

    # Contexte référentiel (optionnel)
    if ctx.referential_name:
        ref_line = f"Référentiel : {ctx.referential_name}"
        if ctx.referential_source_ref:
            ref_line += f" ({ctx.referential_source_ref})"
        system_parts.append("")
        system_parts.append("Contexte référentiel :")
        system_parts.append(f"- {ref_line}")

    if ctx.items_to_focus:
        system_parts.append("- Compétences à travailler :")
        for it in ctx.items_to_focus:
            crit = ", ".join(it.evaluation_criteria[:2]) if it.evaluation_criteria else ""
            ev = ", ".join(it.expected_evidence[:2]) if it.expected_evidence else ""
            line = f"  - {it.code} : {it.title}"
            if crit:
                line += f" | Critères : {crit}"
            if ev:
                line += f" | Preuves attendues : {ev}"
            system_parts.append(line)

    if ctx.items_already_covered:
        system_parts.append("- Compétences déjà travaillées :")
        for it in ctx.items_already_covered:
            system_parts.append(f"  - {it.code} : {it.title}")

    # Contexte apprenant (optionnel)
    if ctx.learner_summary:
        summary = ctx.learner_summary
        if len(summary) > 300:
            summary = summary[:297] + "..."
        system_parts.append("")
        system_parts.append(f"Synthèse récente de la progression : {summary}")

    if ctx.recent_traces_info:
        system_parts.append("Traces récentes : " + " ; ".join(ctx.recent_traces_info))

    # Contexte documents de classe (optionnel)
    if ctx.class_documents:
        docs = ", ".join(ctx.class_documents[:3])
        system_parts.append(f"Documents de classe actifs (titres) : {docs}")

    system_prompt = "\n".join(system_parts)

    # Prompt utilisateur : situation brute + consigne AFEST
    if reflection_phase:
        user_prompt = (
            "Situation décrite par l'apprenant : "
            + content
            + "\n"
            + "En t'appuyant sur le référentiel et le contexte ci-dessus, formule un bloc réflexif court "
            + "(1 constat concret + 1 ou 2 questions courtes), sans faire cours."
        )
    else:
        user_prompt = (
            "Situation décrite par l'apprenant : "
            + content
            + "\n"
            + "En t'appuyant sur le référentiel et le contexte ci-dessus, formule 1 à 2 questions courtes "
            + "pour aider l'apprenant a analyser cette situation (facteurs clés, critères, écarts, pistes de progrès). "
            + "Ne réponds que par des questions."
        )

    return system_prompt, user_prompt


def build_afest_prompts(session: HugoSession, content: str, ctx: HugoContext) -> tuple[str, str]:
    """
    Build (system_prompt, user_prompt) for AFEST Hugo, based on TutorPrompt configuration when available.
    Falls back to the legacy hard-coded behaviour otherwise.
    """
    tutor_prompt = _resolve_tutor_prompt(session)
    if not tutor_prompt:
        return _build_afest_prompts_legacy(session, content, ctx)

    from .prompt_renderer import render_with_tutor_prompt

    rendered = render_with_tutor_prompt(
        tutor_prompt=tutor_prompt,
        session=session,
        ctx=ctx,
        content=content,
    )
    return rendered.system_prompt, rendered.user_prompt

