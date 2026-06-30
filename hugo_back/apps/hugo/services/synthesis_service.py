from __future__ import annotations

from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.hugo.llm_client import complete_with_provider


def _clean_lines(lines: list[str]) -> list[str]:
    return [line for line in (str(item or "").strip() for item in lines) if line]


def _latest_learner_excerpt(session) -> str:
    latest_message = (
        session.messages.filter(role="LEARNER")
        .order_by("-created_at")
        .values_list("content", flat=True)
        .first()
    )
    text = str(latest_message or "").strip()
    if not text:
        return ""
    return text[:280] + ("..." if len(text) > 280 else "")


def _branch_labels(progress) -> list[str]:
    labels = []
    for branch in list(progress.active_branches or [])[:3]:
        label = str(branch.theme_label or branch.objective_label or "").strip()
        if label:
            labels.append(label)
    return labels


def _resolve_provider(session) -> str:
    group = getattr(session, "group", None)
    llm_backend = getattr(group, "llm_backend", "") if group is not None else ""
    if llm_backend:
        return str(llm_backend).strip().lower()
    return str(getattr(settings, "LLM_PROVIDER_DEFAULT", "ollama") or "ollama").strip().lower()


def _recent_conversation_excerpt(session, limit: int = 6) -> str:
    messages = list(
        session.messages.order_by("-created_at").values_list("role", "content")[:limit]
    )
    if not messages:
        return ""
    lines: list[str] = []
    for role, content in reversed(messages):
        speaker = "Hugo" if role == "ASSISTANT" else "Apprenant"
        text = " ".join(str(content or "").split()).strip()
        if not text:
            continue
        if len(text) > 280:
            text = text[:277].rstrip() + "..."
        lines.append(f"- {speaker}: {text}")
    return "\n".join(lines)


def _fallback_synthesis_payload(progress, excerpt: str, branch_labels: list[str], missing_items: list[str]) -> dict[str, Any]:
    lines = [
        "La scène est suffisamment stabilisée pour produire un mini-bilan.",
    ]
    if branch_labels:
        lines.append(f"Fil(s) actif(s) : {', '.join(branch_labels)}.")
    if excerpt:
        lines.append(f"Dernier repère exprimé : {excerpt}")
    if missing_items:
        lines.append(f"Points à garder ouverts : {' ; '.join(missing_items)}.")
    else:
        lines.append("Aucun point bloquant majeur n'est encore remonté dans le contrat de progression.")

    return {
        "title": "Synthèse de la scène",
        "text": "\n".join(lines),
        "reason_codes": list(progress.reason_codes or []),
        "share_recommended": bool(progress.synthesis_eligible),
        "generated_at": timezone.now().isoformat(),
        "source": "fallback",
    }


def _build_synthesis_prompts(session, progress, excerpt: str, branch_labels: list[str], missing_items: list[str]) -> tuple[str, str]:
    system_prompt = (
        "Tu es Hugo. Tu produis une synthèse courte, utile et partageable d'une séance AFEST. "
        "Tu n'exposes jamais de signaux P0, tu ne mentionnes pas d'heuristiques internes, "
        "et tu restes factuel, pédagogique et orienté action. "
        "Réponds en français simple avec 2 à 4 phrases maximum."
    )
    user_lines = [
        "Prépare un mini-bilan métier lisible pour l'apprenant.",
        f"Posture: {getattr(progress.posture, 'value', 'reflective_afest')}",
        f"Maturité: {getattr(progress.overall_maturity, 'value', 'red')}",
    ]
    if branch_labels:
        user_lines.append(f"Fils actifs: {', '.join(branch_labels)}")
    if excerpt:
        user_lines.append(f"Dernier repère apprenant: {excerpt}")
    if missing_items:
        user_lines.append(f"Points encore ouverts: {' ; '.join(missing_items)}")
    if progress.reason_codes:
        user_lines.append(f"Codes raison utiles: {', '.join(progress.reason_codes)}")
    history = _recent_conversation_excerpt(session)
    if history:
        user_lines.append("Historique récent:")
        user_lines.append(history)
    user_lines.append(
        "Retourne uniquement le texte final de la synthèse, sans titre, sans puces JSON, sans préambule."
    )
    return system_prompt, "\n".join(user_lines)


def _clean_llm_text(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return ""
    return clean[:1200].rstrip()


def generate_synthesis(session, progress) -> dict:
    branch_labels = _branch_labels(progress)
    missing_items = _clean_lines(list(progress.missing_for_next_level or [])[:3])
    excerpt = _latest_learner_excerpt(session)
    fallback_payload = _fallback_synthesis_payload(progress, excerpt, branch_labels, missing_items)
    system_prompt, user_prompt = _build_synthesis_prompts(session, progress, excerpt, branch_labels, missing_items)
    provider = _resolve_provider(session)
    text, llm_meta = complete_with_provider(
        prompt=user_prompt,
        system=system_prompt,
        max_tokens=220,
        provider=provider,
        tutor_prompt=getattr(session, "tutor_prompt", None),
    )
    clean_text = _clean_llm_text(text)
    if not clean_text:
        return {
            **fallback_payload,
            "llm_meta": llm_meta,
        }

    return {
        "title": "Synthèse de la scène",
        "text": clean_text,
        "reason_codes": list(progress.reason_codes or []),
        "share_recommended": bool(progress.synthesis_eligible),
        "generated_at": timezone.now().isoformat(),
        "source": "llm",
        "llm_meta": llm_meta,
    }


def generate_evaluation(session, progress) -> dict:
    branch_labels = _branch_labels(progress)
    competence_items = [
        {
            "label": label,
            "status": getattr(branch.exploration_level, "value", "red"),
        }
        for label, branch in zip(branch_labels, list(progress.active_branches or [])[:3], strict=False)
    ]
    validation_candidates = _clean_lines(list(progress.missing_for_next_level or [])[:3])
    excerpt = _latest_learner_excerpt(session)

    lines = [
        "Les apprentissages peuvent être relus à partir de la progression courante.",
    ]
    if competence_items:
        lines.append(
            "Repères évaluables : "
            + ", ".join(f"{item['label']} ({item['status']})" for item in competence_items)
            + "."
        )
    if excerpt:
        lines.append(f"Dernier élément pris en compte : {excerpt}")
    if validation_candidates:
        lines.append(f"Vigilances avant validation : {' ; '.join(validation_candidates)}.")
    else:
        lines.append("Aucune vigilance bloquante n'est remontée par le contrat courant.")

    return {
        "title": "Évaluation des apprentissages",
        "text": "\n".join(lines),
        "competence_items": competence_items,
        "validation_candidates": validation_candidates,
        "reason_codes": list(progress.reason_codes or []),
        "generated_at": timezone.now().isoformat(),
    }
