from __future__ import annotations

from apps.hugo.domain.conversation_profile import ConversationProgress, SessionMaturityLevel
from apps.hugo.domain.reason_codes import (
    RC_DISPERSION_RISK,
    RC_EVALUATION_BLOCKED_COGNITIVE_LOAD,
    RC_EVALUATION_BLOCKED_INTERACTION_RISK,
    RC_EVALUATION_BLOCKED_MATURITY,
    RC_EVALUATION_BLOCKED_RECENT_BILAN,
    RC_LOOP_RISK_HIGH,
    RC_NO_CAUSE_NAMED,
    RC_NO_CONCRETE_ACTIONS,
    RC_NO_TRANSFER_RULE,
    RC_NOT_ENOUGH_DESCRIPTION,
    RC_SYNTHESIS_BLOCKED_MATURITY,
)

_REASON_CODE_MESSAGES: dict[str, str] = {
    RC_NOT_ENOUGH_DESCRIPTION: "Décrivez davantage la situation vécue.",
    RC_NO_CONCRETE_ACTIONS: "Nommez des actions concrètes déjà réalisées.",
    RC_NO_CAUSE_NAMED: "Identifiez une cause plausible ou un point qui bloque.",
    RC_NO_TRANSFER_RULE: "Formulez une règle ou une prochaine action transférable.",
    RC_LOOP_RISK_HIGH: "Stabilisez le fil avant de demander une évaluation.",
    RC_DISPERSION_RISK: "Recentrez la conversation sur un fil principal.",
    RC_EVALUATION_BLOCKED_MATURITY: "La scène doit être plus stabilisée avant une évaluation utile.",
    RC_EVALUATION_BLOCKED_COGNITIVE_LOAD: "Allégez le fil avant de demander une évaluation.",
    RC_EVALUATION_BLOCKED_INTERACTION_RISK: "Clarifiez la situation avant de demander une évaluation.",
    RC_EVALUATION_BLOCKED_RECENT_BILAN: "Poursuivez la conversation avant une nouvelle évaluation.",
    RC_SYNTHESIS_BLOCKED_MATURITY: "La scène doit progresser avant une synthèse utile.",
}

_P0_TOKEN_RE = (
    "episode_clarity",
    "cognitive_load",
    "interaction_risk",
    "problem_salience",
    "reflection_phase",
    "turn_state",
    "p0",
)


def _is_readable_reason(text: str) -> bool:
    normalized = str(text or "").strip()
    if not normalized:
        return False
    lowered = normalized.lower()
    return not any(token in lowered for token in _P0_TOKEN_RE)


def _unique_messages(items: list[str], limit: int = 4) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        message = str(item or "").strip()
        if not message or not _is_readable_reason(message):
            continue
        key = message.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(message)
        if len(result) >= limit:
            break
    return result


def build_blocking_reasons_from_progress(progress: ConversationProgress) -> list[str]:
    candidates: list[str] = []
    candidates.extend(list(progress.missing_for_next_level or []))
    for code in list(progress.reason_codes or []):
        mapped = _REASON_CODE_MESSAGES.get(str(code or "").strip())
        if mapped:
            candidates.append(mapped)
    if progress.active_branches_count == 0:
        candidates.append("La conversation n'est pas encore assez avancée.")
    if not progress.evaluation_eligible and progress.overall_maturity == SessionMaturityLevel.RED:
        candidates.append("La scène doit être plus stabilisée avant une évaluation utile.")
    if not candidates:
        candidates.append("Poursuivez la conversation pour débloquer cette action.")
    return _unique_messages(candidates)


def build_synthesis_blocking_reasons(progress: ConversationProgress) -> list[str]:
    candidates: list[str] = []
    candidates.extend(list(progress.missing_for_next_level or []))
    for code in list(progress.reason_codes or []):
        if code == RC_SYNTHESIS_BLOCKED_MATURITY:
            candidates.append(_REASON_CODE_MESSAGES[RC_SYNTHESIS_BLOCKED_MATURITY])
    if progress.active_branches_count == 0:
        candidates.append("Décrivez davantage la situation pour préparer une synthèse.")
    if not candidates:
        candidates.append("La scène doit progresser avant une synthèse utile.")
    return _unique_messages(candidates)


def resolve_synthesis_ready_status(progress: ConversationProgress) -> tuple[str, list[str]]:
    if progress.synthesis_eligible:
        return "eligible", []
    if progress.active_branches_count == 0:
        return "blocked_not_enough_content", build_synthesis_blocking_reasons(progress)
    return "blocked_context_incomplete", build_synthesis_blocking_reasons(progress)


def resolve_evaluation_ready_status(
    progress: ConversationProgress,
    *,
    allow_early_trigger: bool,
) -> tuple[str, list[str]]:
    if progress.evaluation_eligible:
        return "eligible", []
    if allow_early_trigger:
        return "eligible", []
    reasons = build_blocking_reasons_from_progress(progress)
    if progress.active_branches_count == 0:
        return "blocked_min_turns_not_reached", reasons
    if progress.missing_for_next_level:
        return "blocked_context_incomplete", reasons
    if progress.overall_maturity == SessionMaturityLevel.RED:
        return "blocked_missing_data", reasons
    return "blocked_other", reasons


def can_request_evaluation(session, progress: ConversationProgress, *, allow_early_trigger: bool) -> tuple[bool, list[str]]:
    if progress.evaluation_eligible:
        return True, []
    if allow_early_trigger:
        return True, []
    return False, build_blocking_reasons_from_progress(progress)
