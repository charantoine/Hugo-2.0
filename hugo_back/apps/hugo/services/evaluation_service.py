from __future__ import annotations

import json
import re
from typing import Any

from apps.hugo.domain.conversation_profile import ConversationProgress, SessionMaturityLevel
from apps.hugo.domain.evaluation_profiles import get_evaluation_profile
from apps.hugo.llm_client import complete_with_provider
from apps.hugo.models import EvaluationPolicy, LearnerEvaluationRecord, TrainerKnowledgeItem
from apps.hugo.services.evaluation_workflow_engine import EvaluationContext, assemble_evaluation_context

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


def get_or_create_policy(organisation, group=None) -> EvaluationPolicy:
    policy, _ = EvaluationPolicy.objects.get_or_create(
        organisation=organisation,
        group=group,
        defaults={
            "share_with_tutor": True,
            "tutor_validation_required": False,
            "allow_early_trigger": True,
        },
    )
    return policy


def resolve_evaluation_readiness(progress: ConversationProgress) -> dict[str, Any]:
    maturity = progress.overall_maturity
    if maturity == SessionMaturityLevel.GREEN:
        return {"trigger_state": "green", "message": None, "can_trigger": True}
    if maturity == SessionMaturityLevel.ORANGE:
        return {
            "trigger_state": "orange",
            "message": "La conversation est encore partielle. L'évaluation sera prudente.",
            "can_trigger": True,
        }
    return {
        "trigger_state": "red",
        "message": "La conversation est prématurée pour une validation forte. L'évaluation restera très partielle.",
        "can_trigger": True,
    }


def _fallback_referential_items(progress: ConversationProgress) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for branch in list(progress.active_branches or [])[:6]:
        label = str(branch.objective_label or branch.theme_label or "Critère de progression").strip()
        items.append(
            {
                "id": str(branch.referential_item_id or branch.branch_id or label),
                "label": label,
                "theme": str(branch.theme_label or "").strip(),
            }
        )
    return items


def _validated_trainer_items(session, limit: int = 20) -> list[dict[str, Any]]:
    qs = TrainerKnowledgeItem.objects.filter(
        organisation=session.organisation,
        status="validated_trainer",
    ).order_by("-updated_at")[:limit]
    return list(qs.values("id", "content", "content_type", "referential_item_id"))


def _recent_history(session, limit: int = 10) -> list[dict[str, str]]:
    history = session.messages.order_by("-created_at").values("role", "content")[:limit]
    normalized: list[dict[str, str]] = []
    for item in reversed(list(history)):
        role = "assistant" if item["role"] == "ASSISTANT" else "user"
        normalized.append({"role": role, "content": str(item["content"] or "")[:300]})
    return normalized


def build_evaluation_prompt(context: EvaluationContext, profile: dict[str, Any], conversation_history: list[dict[str, str]]) -> tuple[str, str]:
    system_prompt = "\n".join(
        [
            profile["prompt_frame"],
            "",
            profile["prompt_judgement_guide"],
            "",
            profile["prompt_output_guide"],
            "",
            "Ne retourne que du JSON valide, sans commentaire hors JSON.",
        ]
    ).strip()

    lines = ["Contexte d'évaluation :"]
    if context.trainer_directives:
        lines.extend(["Directives formateur :", context.trainer_directives, ""])
    if context.referential_items:
        lines.append("Critères ciblés :")
        for item in context.referential_items:
            lines.append(f"- [{item.get('id', '')}] {item.get('label', '')}")
        lines.append("")
    if context.trainer_knowledge_items:
        lines.append("Connaissances formateur validées :")
        for item in context.trainer_knowledge_items[:8]:
            lines.append(f"- ({item.get('content_type', '')}) {str(item.get('content', ''))[:220]}")
        lines.append("")
    if context.conversation_evidence:
        lines.append("Indices conversationnels :")
        for evidence in context.conversation_evidence:
            lines.append(
                f"- {evidence.get('theme', '')} / {evidence.get('objective', '')} "
                f"(maturité={evidence.get('maturity', '')})"
            )
        lines.append("")
    if context.is_early_trigger:
        lines.append("Important: l'apprenant a déclenché l'évaluation avant la maturité recommandée.")
        lines.append("")
    if conversation_history:
        lines.append("Historique récent :")
        for message in conversation_history:
            lines.append(f"- [{message.get('role', '?')}] {message.get('content', '')}")

    return system_prompt, "\n".join(lines).strip()


def _fallback_evaluation_output(progress: ConversationProgress, referential_items: list[dict[str, Any]]) -> dict[str, Any]:
    branches = list(progress.active_branches or [])
    items: list[dict[str, Any]] = []
    for index, item in enumerate(referential_items[:6]):
        branch = branches[index] if index < len(branches) else None
        maturity = getattr(getattr(branch, "exploration_level", None), "value", progress.overall_maturity.value)
        positioning_level = {
            "red": "not_covered",
            "orange": "partial",
            "green": "demonstrated",
        }.get(maturity, "partial")
        items.append(
            {
                "target_item_id": str(item.get("id") or f"item-{index}"),
                "label": str(item.get("label") or item.get("theme") or "Critère"),
                "positioning_level": positioning_level,
                "evidence_basis": str(item.get("theme") or item.get("label") or "Indice de progression observé."),
                "confidence": 0.8 if positioning_level == "demonstrated" else 0.55,
                "missing_evidence": list(progress.missing_for_next_level[:2]) if positioning_level != "demonstrated" else [],
                "learner_self_position": "",
                "status": "draft",
            }
        )

    overall_status = "early_trigger" if progress.overall_maturity != SessionMaturityLevel.GREEN else "complete"
    recap_text = (
        "L'évaluation reste partielle car la scène n'est pas encore totalement stabilisée."
        if overall_status == "early_trigger"
        else "L'évaluation confirme des acquis déjà visibles dans la progression courante."
    )
    return {
        "overall_status": overall_status,
        "recap_text": recap_text,
        "items": items,
        "first_message": recap_text,
    }


def _extract_json_payload(text: str) -> dict[str, Any] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    match = JSON_BLOCK_RE.search(raw)
    if match:
        raw = match.group(1).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None


def _normalize_item(item: dict[str, Any], default_id: str) -> dict[str, Any]:
    positioning_level = str(item.get("positioning_level") or "partial").strip().lower()
    if positioning_level not in {"not_covered", "partial", "demonstrated", "mastered"}:
        positioning_level = "partial"
    confidence = item.get("confidence", 0.5)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5
    return {
        "target_item_id": str(item.get("target_item_id") or default_id),
        "label": str(item.get("label") or "Critère").strip(),
        "positioning_level": positioning_level,
        "evidence_basis": str(item.get("evidence_basis") or "").strip(),
        "confidence": max(0.0, min(1.0, confidence)),
        "missing_evidence": [str(v).strip() for v in list(item.get("missing_evidence") or []) if str(v).strip()],
        "learner_self_position": str(item.get("learner_self_position") or "").strip(),
        "status": str(item.get("status") or "draft").strip() or "draft",
    }


def _normalize_evaluation_output(payload: dict[str, Any] | None, fallback: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return fallback
    raw_items = list(payload.get("items") or [])
    items = [
        _normalize_item(item, default_id=f"item-{index}")
        for index, item in enumerate(raw_items)
        if isinstance(item, dict)
    ]
    if not items:
        items = list(fallback["items"])
    overall_status = str(payload.get("overall_status") or fallback["overall_status"]).strip().lower()
    if overall_status not in {"partial", "complete", "early_trigger"}:
        overall_status = fallback["overall_status"]
    recap_text = str(payload.get("recap_text") or fallback["recap_text"]).strip()
    first_message = str(payload.get("first_message") or recap_text).strip()
    return {
        "overall_status": overall_status,
        "recap_text": recap_text,
        "items": items,
        "first_message": first_message,
    }


def generate_evaluation_payload(session, progress: ConversationProgress) -> dict[str, Any]:
    policy = get_or_create_policy(session.organisation, session.group)
    readiness = resolve_evaluation_readiness(progress)
    is_early = readiness["trigger_state"] != "green"
    profile_code = policy.evaluation_profile_code or ("early_trigger" if is_early else "default")
    profile = get_evaluation_profile(session.organisation, code=profile_code, is_early_trigger=is_early)
    referential_items = _fallback_referential_items(progress)
    trainer_items = _validated_trainer_items(session)
    history = _recent_history(session)
    context = assemble_evaluation_context(
        session=session,
        progress=progress,
        policy=policy,
        referential_items=referential_items,
        trainer_knowledge_items=trainer_items,
    )
    system_prompt, user_prompt = build_evaluation_prompt(context, profile, history)
    fallback = _fallback_evaluation_output(progress, referential_items)
    text, llm_meta = complete_with_provider(
        prompt=user_prompt,
        system=system_prompt,
        max_tokens=420,
        provider=str(getattr(getattr(session, "group", None), "llm_backend", "") or "ollama").lower(),
        tutor_prompt=getattr(session, "tutor_prompt", None),
    )
    payload = _normalize_evaluation_output(_extract_json_payload(text), fallback)
    payload["profile_code"] = str(profile.get("name") or profile_code)
    payload["trigger_state"] = readiness["trigger_state"]
    payload["warning"] = readiness.get("message")
    payload["llm_meta"] = llm_meta
    return payload


def save_evaluation_record(session, progress: ConversationProgress, evaluation_output: dict[str, Any]) -> LearnerEvaluationRecord:
    policy = get_or_create_policy(session.organisation, session.group)
    overall_status = str(evaluation_output.get("overall_status") or "partial").strip().lower()
    if progress.overall_maturity != SessionMaturityLevel.GREEN:
        overall_status = "early_trigger"
    record, _ = LearnerEvaluationRecord.objects.update_or_create(
        session=session,
        defaults={
            "organisation": session.organisation,
            "learner": session.learner,
            "group": session.group,
            "overall_status": overall_status,
            "items": list(evaluation_output.get("items") or []),
            "recap_text": str(evaluation_output.get("recap_text") or "").strip(),
            "evaluation_profile_used": str(evaluation_output.get("profile_code") or "default"),
            "shared_with_tutor": bool(policy.share_with_tutor),
            "trigger_maturity": progress.overall_maturity.value,
        },
    )
    return record


def build_evaluation_preview(record: LearnerEvaluationRecord, evaluation_output: dict[str, Any]) -> dict[str, Any]:
    validation_candidates = []
    for item in list(record.items or []):
        validation_candidates.extend(list(item.get("missing_evidence") or []))
    unique_candidates: list[str] = []
    for candidate in validation_candidates:
        text = str(candidate or "").strip()
        if text and text not in unique_candidates:
            unique_candidates.append(text)
    return {
        "title": "Évaluation des apprentissages",
        "text": str(record.recap_text or evaluation_output.get("first_message") or "").strip(),
        "competence_items": [
            {
                "label": str(item.get("label") or "Critère"),
                "status": str(item.get("positioning_level") or "partial"),
            }
            for item in list(record.items or [])
        ],
        "validation_candidates": unique_candidates[:4],
        "record_id": str(record.id),
        "overall_status": record.overall_status,
        "warning": evaluation_output.get("warning"),
        "first_message": evaluation_output.get("first_message"),
        "profile_name": evaluation_output.get("profile_code", "default"),
    }
