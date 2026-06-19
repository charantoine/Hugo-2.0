from __future__ import annotations

import re
from typing import Any

from apps.hugo.domain.schemas import (
    P0_CORE_FIELDS,
    SESSION_PHASE_DEEPENING,
    SESSION_PHASE_EXPLORATION,
    SESSION_PHASE_OPENING,
    SESSION_PHASE_POTENTIAL_CLOSURE,
    TurnState,
    normalize_session_phase,
)


ACTION_PATTERNS = [
    r"\bj['’]ai\b",
    r"\bje (fais|faisais|faisant|vais|dois|controle|controlee?|verifie|verifiee?|installe|branche|mesure|observe|choisi|decide|corrige|teste)\b",
    r"\bon a\b",
]
TECHNICAL_COMPONENT_PATTERNS = [
    r"\b(disjoncteur|differentiel|différentiel|tableau|radiateur|cablage|câblage|raccordement|terre|phase|neutre)\b",
    r"\b(tension|puissance|intensite|intensité|ampere|ampères?|watt|watts|mesure|controle|contrôle|essai)\b",
    r"\b(consignation|norme|conformite|conformité|procedure|procédure|checklist|autocontr[ôo]le)\b",
]
TECHNICAL_CRITERION_PATTERNS = [
    r"\b(critere|critère|conformite|conformité|norme|procedure|procédure|qualite|qualité|securite|sécurité)\b",
    r"\b(c\d+(?:\.\d+)?|bc\d+|t\d+(?:-\d+)?)\b",
]
SAFETY_OR_QUALITY_HIGH_PATTERNS = [
    r"\b(disjoncte|disjoncter|court[- ]?circuit|electrocution|électrocution|danger|brule|brûle|fumee|fumée)\b",
    r"\b(pas de terre|sans terre|terre absente|absence de terre)\b",
]
SAFETY_OR_QUALITY_MEDIUM_PATTERNS = [
    r"\b(securite|sécurité|risque|qualite|qualité|protection|conformite|conformité|norme)\b",
    r"\b(disjoncteur|differentiel|différentiel|consignation|epi|autocontr[ôo]le|verification|vérification)\b",
]
ANALYSIS_PATTERNS = [
    r"\bparce que\b",
    r"\bdu coup\b",
    r"\b(critere|critère|cause|raison|pourquoi|analyse|j['’]ai choisi|j['’]ai decide)\b",
]
PROJECTION_PATTERNS = [
    r"\bje vais\b",
    r"\bprochaine fois\b",
    r"\bje ferai\b",
    r"\bplan d['’ ]action\b",
]
PROBLEM_HIGH_PATTERNS = [
    r"\b(probleme|problème|incident|panne|erreur|danger|risque|blocage|difficulte|difficulté)\b",
]
PROBLEM_LOW_PATTERNS = [
    r"\bpas simple\b",
    r"\bpas evident\b",
    r"\bj['’]ai hesite\b",
    r"\bj['’]ai h[ée]sit[ée]\b",
]
LOW_EFFICACY_PATTERNS = [
    r"\bje ne sais pas\b",
    r"\bj['’]ai du mal\b",
    r"\bje doute\b",
    r"\bpas sur\b",
    r"\bbesoin d['’ ]aide\b",
    r"\bje n['’]y arrive pas\b",
]
HIGH_EFFICACY_PATTERNS = [
    r"\bj['’]ai reussi\b",
    r"\bje maitrise\b",
    r"\bje suis a l['’]aise\b",
    r"\bje me sens capable\b",
    r"\bj['’]ai bien realise\b",
    r"\bj['’]ai bien reussi\b",
]
NEGATIVE_AFFECT_PATTERNS = [
    r"\b(frustre|frustr[ée]|stresse|stress[ée]|agace|agac[ée]|decu|déçu|peur)\b",
    r"\b(decourage|décourag[ée])\b",
]
POSITIVE_AFFECT_PATTERNS = [
    r"\b(content|satisfait|fi[èe]re?|soulag[ée]|ravi)\b",
    r"\bca s['’]est bien passe\b",
    r"\bj['’]en suis fier\b",
]
HIGH_LOAD_PATTERNS = [
    r"\b(perdu|perdue|sature|satur[ée]|trop d['’ ]infos|il y en a trop)\b",
    r"\bje m['’]embrouille\b",
]
MEDIUM_LOAD_PATTERNS = [
    r"\b(complique|compliqu[ée]|pas simple|beaucoup de choses|charge)\b",
    r"\bje dois tout gerer\b",
]
HIGH_RISK_PATTERNS = [
    r"\b(j['’]en ai marre|laisse tomber|ca m['’]enerve|ça m['’]énerve|c['’]est bon)\b",
]
MEDIUM_RISK_PATTERNS = [
    r"\b(bof|pas envie|je sais pas trop|mouais)\b",
]
NOVICE_PATTERNS = [
    r"\bje debute\b",
    r"\bje decouvre\b",
    r"\bc['’]etait la premiere fois\b",
    r"\bje ne maitrise pas\b",
]
EXPERT_PATTERNS = [
    r"\bca fait \d+ ans\b",
    r"\bj['’]ai l['’]habitude\b",
    r"\bje connais bien\b",
    r"\bc['’]est mon quotidien\b",
]
BELOW_ZPD_PATTERNS = [
    r"\bc['’]etait facile\b",
    r"\bc['’]est simple\b",
    r"\brien de special\b",
]
BEYOND_ZPD_PATTERNS = [
    r"\bc['’]etait trop dur\b",
    r"\bc['’]est trop complique\b",
    r"\bhors de portee\b",
    r"\bimpossible\b",
]
CONTRADICTION_PATTERNS = [
    r"\ben fait\b",
    r"\bfinalement\b",
    r"\bau debut\b.*\bpuis\b",
]
CONTEXT_MARKERS = [
    r"\b(chantier|atelier|client|tableau|machine|procedure|procédure|materiel|matériel|equipe|équipe)\b",
    r"\b(avant|apres|après|pendant|quand|puis|ensuite)\b",
]
CLARIFY_MOVES = {"clarify", "elicit_action"}
POINT_TRACKING_MOVES = {"clarify", "elicit_action", "problematize", "analyze"}
COVERED_POINT_ORDER = [
    "episode_described",
    "concrete_actions_described",
    "problem_named",
    "cause_hypothesis_named",
    "cause_confirmed",
    "future_action_named",
    "learning_rule_named",
    "session_done_explicitly",
]
REMAINING_POINT_ORDER = [
    "missing_episode_details",
    "missing_problem_identification",
    "missing_cause",
    "missing_future_action",
    "missing_transfer_rule",
    "need_closure_confirmation",
    "none",
]
HELP_REQUEST_EXPLICIT_PATTERNS = [
    r"\baide(?:\s|-)?moi\b",
    r"\bje comprends pas\b.*\baide",
    r"\bje sais pas\b.*\baide",
    r"\bdis[- ]?moi\b",
]
HELP_REQUEST_IMPLICIT_PATTERNS = [
    r"\bje ne sais pas\b",
    r"\bje sais pas\b",
    r"\bje vois pas\b",
    r"\bje bloque\b",
]
CLOSURE_SIGNAL_EXPLICIT_PATTERNS = [
    r"\bon a fini\b",
    r"\bc['’]est fini\b",
    r"\bj['’]ai fini\b",
    r"\boui[, ]+deja dit\b",
    r"\boui[, ]+déjà dit\b",
    r"\bnon[, ]+j['’]ai fini\b",
    r"\bon a fait le tour\b",
]
CLOSURE_SIGNAL_IMPLICIT_PATTERNS = [
    r"\bc['’]est regle\b",
    r"\bc['’]est réglé\b",
    r"\bje pense qu['’]on a fait le tour\b",
    r"\bon a fait le tour\b",
]
REPETITION_SIGNAL_EXPLICIT_PATTERNS = [
    r"\bon tourne en rond\b",
    r"\bdeja dit\b",
    r"\bdéjà dit\b",
    r"\bje te l['’]ai deja dit\b",
    r"\bje te l['’]ai déjà dit\b",
]
REPETITION_SIGNAL_IMPLICIT_PATTERNS = [
    r"\bencore\b",
    r"\bje viens de le dire\b",
]
CAUSE_HYPOTHESIS_PATTERNS = [
    r"\bje pense que\b",
    r"\bca doit etre\b",
    r"\bça doit être\b",
    r"\bpeut[- ]etre que\b",
    r"\bpeut-être que\b",
    r"\bparce que\b",
    r"\bj['’]aurais pas du\b",
    r"\bj['’]aurais dû\b",
]
CAUSE_CONFIRMED_PATTERNS = [
    r"\bc['’]etait\b",
    r"\bc['’]était\b",
    r"\ble probleme venait de\b",
    r"\ble problème venait de\b",
    r"\bvenait d['’]un\b",
    r"\bvenait d['’]une\b",
    r"\bun des fils etait\b",
    r"\bun des fils était\b",
    r"\bj['’]ai trouve\b",
    r"\bj['’]ai trouvé\b",
]
LEARNING_RULE_PATTERNS = [
    r"\bil faut\b",
    r"\bdesormais\b",
    r"\bdésormais\b",
    r"\bje retiens que\b",
    r"\bla prochaine fois je verifierai toujours\b",
    r"\bla prochaine fois je vérifierai toujours\b",
]
META_LEAK_RISK_PATTERNS = [
    r"\bconsigne\b",
    r"\bsystem prompt\b",
    r"\bprompt interne\b",
    r"\binstruction\b",
    r"\bdernier message de l['’]apprenant\b",
    r"\bmessage apprenant\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _count_matches(text: str, patterns: list[str]) -> int:
    return sum(1 for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE))


def _message_count(session: Any) -> int:
    try:
        return int(session.messages.count())
    except Exception:
        return 0


def _iter_previous_learner_payloads(session: Any) -> list[dict[str, Any]]:
    try:
        messages = session.messages.filter(role="LEARNER").order_by("-created_at")
    except Exception:
        return []
    payloads: list[dict[str, Any]] = []
    for message in messages:
        payload = getattr(message, "llm_request_payload", None) or {}
        if isinstance(payload, dict) and payload:
            payloads.append(payload)
    return payloads


def _iter_previous_learner_texts(session: Any) -> list[str]:
    try:
        messages = session.messages.filter(role="LEARNER").order_by("-created_at")
    except Exception:
        return []
    texts: list[str] = []
    for idx, message in enumerate(messages):
        payload = getattr(message, "llm_request_payload", None) or {}
        if idx == 0 and not payload:
            # When the current learner message has just been created, it has no payload yet.
            continue
        content = str(getattr(message, "content", "") or "").strip()
        if content:
            texts.append(content)
    return texts


def _previous_turn_signals(session: Any) -> tuple[str, int, bool]:
    payloads = _iter_previous_learner_payloads(session)
    last_move = ""
    consecutive_clarify_turns = 0
    sticky_has_actions = False
    for payload in payloads:
        turn_state = payload.get("turn_state") or {}
        if turn_state.get("has_concrete_actions") is True:
            sticky_has_actions = True
        conversation_decision = payload.get("conversation_decision") or {}
        move = str(conversation_decision.get("pedagogical_move") or "").strip()
        if not last_move and move:
            last_move = move
        if move in CLARIFY_MOVES and consecutive_clarify_turns == 0:
            consecutive_clarify_turns = 1
            continue
        if consecutive_clarify_turns and move in CLARIFY_MOVES:
            consecutive_clarify_turns += 1
            continue
        if consecutive_clarify_turns:
            break
    return last_move, consecutive_clarify_turns, sticky_has_actions


def _ordered_point_list(points: set[str], known_values: list[str]) -> list[str]:
    ordered = [value for value in known_values if value in points]
    extras = sorted(points.difference(ordered))
    return ordered + extras


def _detect_help_request(text: str) -> str:
    if _matches_any(text, HELP_REQUEST_EXPLICIT_PATTERNS):
        return "explicit"
    if _matches_any(text, HELP_REQUEST_IMPLICIT_PATTERNS):
        return "implicit"
    return "none"


def _detect_closure_signal(text: str) -> str:
    if _matches_any(text, CLOSURE_SIGNAL_EXPLICIT_PATTERNS):
        return "explicit"
    if _matches_any(text, CLOSURE_SIGNAL_IMPLICIT_PATTERNS):
        return "implicit"
    return "none"


def _detect_repetition_signal(text: str) -> str:
    if _matches_any(text, REPETITION_SIGNAL_EXPLICIT_PATTERNS):
        return "explicit"
    if _matches_any(text, REPETITION_SIGNAL_IMPLICIT_PATTERNS):
        return "implicit"
    return "none"


def _infer_covered_points_from_text(
    text: str,
    *,
    has_concrete_actions: bool = False,
    episode_clarity: str = "",
    problem_salience: str = "",
    reflection_phase: str = "",
    closure_signal: str = "none",
) -> set[str]:
    covered: set[str] = set()
    if episode_clarity in {"medium", "high"} or len(text.split()) >= 12 or _count_matches(text, CONTEXT_MARKERS) >= 1:
        covered.add("episode_described")
    if has_concrete_actions or _matches_any(text, ACTION_PATTERNS):
        covered.update({"episode_described", "concrete_actions_described"})
    if (
        problem_salience in {"low", "high"}
        or _matches_any(text, PROBLEM_HIGH_PATTERNS)
        or _matches_any(text, SAFETY_OR_QUALITY_HIGH_PATTERNS)
    ):
        covered.add("problem_named")
    if reflection_phase == "analysis" or _matches_any(text, CAUSE_HYPOTHESIS_PATTERNS):
        covered.add("cause_hypothesis_named")
    if _matches_any(text, CAUSE_CONFIRMED_PATTERNS):
        covered.add("cause_confirmed")
    if reflection_phase == "projection" or _matches_any(text, PROJECTION_PATTERNS):
        covered.add("future_action_named")
    if _matches_any(text, LEARNING_RULE_PATTERNS):
        covered.add("learning_rule_named")
    if closure_signal == "explicit" or _matches_any(text, CLOSURE_SIGNAL_EXPLICIT_PATTERNS):
        covered.add("session_done_explicitly")
    return covered


def _previous_covered_points(session: Any) -> set[str]:
    covered: set[str] = set()
    for payload in _iter_previous_learner_payloads(session):
        turn_state = payload.get("turn_state") or {}
        for value in list(turn_state.get("covered_points") or []):
            if isinstance(value, str) and value.strip():
                covered.add(value.strip())
    for text in _iter_previous_learner_texts(session):
        covered.update(_infer_covered_points_from_text(text))
    return covered


def _compute_remaining_open_points(
    *,
    covered_points: set[str],
    episode_clarity: str,
    closure_signal: str,
    safety_or_quality_risk_level: str,
) -> list[str]:
    if closure_signal == "explicit" and safety_or_quality_risk_level != "high":
        return ["none"]
    remaining: set[str] = set()
    if "episode_described" not in covered_points or episode_clarity == "low":
        remaining.add("missing_episode_details")
    if "problem_named" not in covered_points and safety_or_quality_risk_level == "low":
        remaining.add("missing_problem_identification")
    if "cause_hypothesis_named" not in covered_points and "cause_confirmed" not in covered_points:
        remaining.add("missing_cause")
    if "future_action_named" not in covered_points:
        remaining.add("missing_future_action")
    if "learning_rule_named" not in covered_points:
        remaining.add("missing_transfer_rule")
    can_close_from_coverage = (
        "episode_described" in covered_points
        and bool(
            {"cause_hypothesis_named", "cause_confirmed", "future_action_named", "learning_rule_named"}
            & covered_points
        )
    )
    if closure_signal == "implicit" or can_close_from_coverage:
        remaining.add("need_closure_confirmation")
    if not remaining:
        return ["none"]
    return _ordered_point_list(remaining, REMAINING_POINT_ORDER)


def _compute_loop_risk(
    *,
    repetition_signal: str,
    last_tutorial_move: str,
    consecutive_clarify_turns: int,
    previous_covered_points: set[str],
    current_covered_points: set[str],
) -> str:
    if repetition_signal == "explicit":
        return "high"
    new_points = current_covered_points.difference(previous_covered_points)
    if not new_points and last_tutorial_move in POINT_TRACKING_MOVES and previous_covered_points:
        return "high"
    if repetition_signal == "implicit" or consecutive_clarify_turns >= 1:
        return "medium"
    return "low"


def _compute_assistant_meta_leak_risk(text: str) -> str:
    return "high" if _matches_any(text, META_LEAK_RISK_PATTERNS) else "low"


def _compute_episode_clarity(text: str, has_concrete_actions: bool) -> str:
    marker_count = _count_matches(text, CONTEXT_MARKERS)
    if has_concrete_actions and marker_count >= 2 and len(text.split()) >= 20:
        return "high"
    if has_concrete_actions or marker_count >= 1 or len(text.split()) >= 12:
        return "medium"
    return "low"


def _compute_reflection_phase(text: str) -> str:
    if _matches_any(text, PROJECTION_PATTERNS):
        return "projection"
    if _matches_any(text, ANALYSIS_PATTERNS):
        return "analysis"
    return "description"


def _compute_tech_representation_level(text: str) -> str:
    technical_hits = _count_matches(text, TECHNICAL_COMPONENT_PATTERNS)
    criterion_hits = _count_matches(text, TECHNICAL_CRITERION_PATTERNS)
    if technical_hits >= 2 and criterion_hits >= 1:
        return "explicit"
    if technical_hits >= 1:
        return "partial"
    return "implicit"


def _compute_technical_criterion_focus(text: str, ctx: Any) -> str:
    if _matches_any(text, TECHNICAL_CRITERION_PATTERNS):
        return "explicit"
    candidate_items = list(getattr(ctx, "items_to_focus", []) or [])[:2]
    lowered = text.lower()
    for item in candidate_items:
        for criterion in list(getattr(item, "criteria", []) or [])[:3]:
            label = str(getattr(criterion, "label", "") or "").lower()
            label_tokens = [token for token in re.findall(r"[a-zA-ZÀ-ÿ0-9_]+", label) if len(token) >= 5]
            if any(token in lowered for token in label_tokens[:4]):
                return "implicit"
    return "none"


def _compute_safety_or_quality_risk_level(text: str) -> str:
    if _matches_any(text, SAFETY_OR_QUALITY_HIGH_PATTERNS):
        return "high"
    if _matches_any(text, SAFETY_OR_QUALITY_MEDIUM_PATTERNS):
        return "medium"
    return "low"


def _compute_reflective_depth(text: str, reflection_phase: str) -> str:
    analysis_count = _count_matches(text, ANALYSIS_PATTERNS)
    if reflection_phase == "analysis" and analysis_count >= 2:
        return "high"
    if reflection_phase in {"analysis", "projection"} or analysis_count >= 1:
        return "medium"
    return "low"


def _compute_session_phase(base_phase: str, reflection_phase: str, evidence_strength: str) -> str:
    if base_phase == SESSION_PHASE_OPENING:
        return SESSION_PHASE_OPENING
    if base_phase == SESSION_PHASE_POTENTIAL_CLOSURE:
        return SESSION_PHASE_POTENTIAL_CLOSURE
    if reflection_phase == "analysis":
        return SESSION_PHASE_DEEPENING
    if reflection_phase == "projection" and evidence_strength in {"medium", "high"}:
        return SESSION_PHASE_POTENTIAL_CLOSURE
    return SESSION_PHASE_EXPLORATION


def _recent_progress_from_summary(summary: str | None, trace_count: int) -> str:
    text = str(summary or "").lower()
    if "bloqu" in text or "retard" in text:
        return "stalled"
    if "progress" in text or "avance" in text or "stable" in text:
        return "steady"
    if trace_count >= 3:
        return "steady"
    return "unclear"


def _recent_progress_from_content(content: str) -> str | None:
    text = str(content or "").lower()
    if any(term in text for term in ["j'ai progresse", "j ai progresse", "j'avance", "j avance", "mieux que"]):
        return "improving"
    if any(term in text for term in ["je bloque", "j'ai bloque", "j ai bloque", "j'y arrive pas", "j y arrive pas"]):
        return "stalled"
    if any(term in text for term in ["comme d'habitude", "comme d habitude", "stable"]):
        return "steady"
    return None


def _coerce_state_override(field_name: str, value: Any) -> Any:
    if field_name == "has_concrete_actions":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "oui"}
    return value


def _debug_signal_payload(
    *,
    base_phase: str,
    total_turns: int,
    recent_traces: list[Any],
    state_overrides: dict[str, Any] | None = None,
    debug_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "base_phase": base_phase,
        "message_count": total_turns,
        "recent_traces_count": len(recent_traces),
    }
    if state_overrides:
        payload["override_fields"] = sorted(state_overrides.keys())
    if debug_overrides:
        payload.update(debug_overrides)
    return payload


def analyze_turn_state(
    session: Any,
    user_input: dict[str, Any],
    ctx: Any,
    *,
    state_overrides: dict[str, Any] | None = None,
    debug_overrides: dict[str, Any] | None = None,
) -> TurnState:
    content = str(user_input.get("content") or "").strip()
    base_phase = normalize_session_phase(
        user_input.get("session_phase") or getattr(session, "current_phase", None)
    )
    overrides = {
        key: _coerce_state_override(key, value)
        for key, value in (state_overrides or {}).items()
        if key in P0_CORE_FIELDS
    }
    last_tutorial_move, consecutive_clarify_turns, sticky_session_actions = _previous_turn_signals(session)
    previous_covered_points = _previous_covered_points(session)
    raw_has_concrete_actions = overrides.get("has_concrete_actions", _matches_any(content, ACTION_PATTERNS))
    has_concrete_actions = bool(raw_has_concrete_actions or sticky_session_actions)
    episode_clarity = overrides.get(
        "episode_clarity",
        _compute_episode_clarity(content, has_concrete_actions),
    )

    if "problem_salience" in overrides:
        problem_salience = overrides["problem_salience"]
    elif _matches_any(content, PROBLEM_HIGH_PATTERNS):
        problem_salience = "high"
    elif _matches_any(content, PROBLEM_LOW_PATTERNS):
        problem_salience = "low"
    else:
        problem_salience = "none"

    reflection_phase = overrides.get("reflection_phase", _compute_reflection_phase(content))
    reflective_depth = overrides.get(
        "reflective_depth",
        _compute_reflective_depth(content, reflection_phase),
    )

    if "self_efficacy_signal" in overrides:
        self_efficacy_signal = overrides["self_efficacy_signal"]
    elif _matches_any(content, LOW_EFFICACY_PATTERNS):
        self_efficacy_signal = "low"
    elif _matches_any(content, HIGH_EFFICACY_PATTERNS):
        self_efficacy_signal = "high"
    else:
        self_efficacy_signal = "neutral"

    if "affect_valence" in overrides:
        affect_valence = overrides["affect_valence"]
    elif _matches_any(content, NEGATIVE_AFFECT_PATTERNS):
        affect_valence = "negative"
    elif _matches_any(content, POSITIVE_AFFECT_PATTERNS):
        affect_valence = "positive"
    else:
        affect_valence = "neutral"

    if "cognitive_load" in overrides:
        cognitive_load = overrides["cognitive_load"]
    elif _matches_any(content, HIGH_LOAD_PATTERNS):
        cognitive_load = "high"
    elif _matches_any(content, MEDIUM_LOAD_PATTERNS):
        cognitive_load = "medium"
    else:
        cognitive_load = "low"

    if "interaction_risk" in overrides:
        interaction_risk = overrides["interaction_risk"]
    elif _matches_any(content, HIGH_RISK_PATTERNS):
        interaction_risk = "high"
    elif _matches_any(content, MEDIUM_RISK_PATTERNS):
        interaction_risk = "medium"
    else:
        interaction_risk = "low"

    if "epistemic_balance" in overrides:
        epistemic_balance = overrides["epistemic_balance"]
    elif _matches_any(content, EXPERT_PATTERNS):
        epistemic_balance = "learner_more_expert"
    elif _matches_any(content, NOVICE_PATTERNS):
        epistemic_balance = "tutor_more_expert"
    else:
        epistemic_balance = "balanced"

    if "zpd_estimate" in overrides:
        zpd_estimate = overrides["zpd_estimate"]
    elif _matches_any(content, BELOW_ZPD_PATTERNS):
        zpd_estimate = "below"
    elif _matches_any(content, BEYOND_ZPD_PATTERNS) or cognitive_load == "high":
        zpd_estimate = "beyond"
    else:
        zpd_estimate = "in"

    if "evidence_strength" in overrides:
        evidence_strength = overrides["evidence_strength"]
    elif episode_clarity == "high" and has_concrete_actions and reflection_phase in {"analysis", "projection"}:
        evidence_strength = "high"
    elif episode_clarity in {"medium", "high"} and has_concrete_actions:
        evidence_strength = "medium"
    else:
        evidence_strength = "low"

    total_turns = _message_count(session)
    recent_traces = list(getattr(ctx, "recent_traces_info", []) or [])
    if "session_maturity" in overrides:
        session_maturity = overrides["session_maturity"]
    elif total_turns >= 8 or len(recent_traces) >= 3:
        session_maturity = "high"
    elif total_turns >= 4 or len(recent_traces) >= 1:
        session_maturity = "medium"
    else:
        session_maturity = "low"

    session_phase = overrides.get(
        "session_phase",
        _compute_session_phase(base_phase, reflection_phase, evidence_strength),
    )

    if "intervention_necessity" in overrides:
        intervention_necessity = overrides["intervention_necessity"]
    elif episode_clarity == "low" or not has_concrete_actions or problem_salience == "high":
        intervention_necessity = "high"
    elif cognitive_load == "high" or interaction_risk == "high":
        intervention_necessity = "high"
    elif problem_salience == "low" or reflective_depth == "low":
        intervention_necessity = "low"
    else:
        intervention_necessity = "none"

    contradiction_status = overrides.get(
        "contradiction_status",
        "suspected" if _matches_any(content, CONTRADICTION_PATTERNS) else "none",
    )
    concept_clarity = "high" if reflective_depth == "high" else ("medium" if reflection_phase == "analysis" else "low")

    material_score = 0
    if getattr(ctx, "learner_summary", None):
        material_score += 1
    if recent_traces:
        material_score += 1
    if getattr(ctx, "class_documents", None):
        material_score += 1
    available_material = "high" if material_score >= 3 else ("medium" if material_score >= 1 else "low")

    if episode_clarity == "low":
        conversation_goal = "clarify_episode"
    elif not has_concrete_actions:
        conversation_goal = "elicit_concrete_action"
    elif session_phase == SESSION_PHASE_POTENTIAL_CLOSURE:
        conversation_goal = "close_or_project"
    elif reflection_phase == "analysis":
        conversation_goal = "deepen_analysis"
    else:
        conversation_goal = "structure_description"

    if cognitive_load == "high" or zpd_estimate == "beyond":
        action_feasibility = "low"
    elif has_concrete_actions and self_efficacy_signal == "high":
        action_feasibility = "high"
    else:
        action_feasibility = "medium"

    if self_efficacy_signal == "high" and epistemic_balance != "tutor_more_expert":
        autonomy_level = "high"
    elif self_efficacy_signal == "low":
        autonomy_level = "low"
    else:
        autonomy_level = "medium"

    recent_progress = _recent_progress_from_content(content) or _recent_progress_from_summary(
        getattr(ctx, "learner_summary", None), len(recent_traces)
    )
    tech_representation_level = _compute_tech_representation_level(content)
    technical_criterion_focus = _compute_technical_criterion_focus(content, ctx)
    safety_or_quality_risk_level = _compute_safety_or_quality_risk_level(content)
    learner_help_request = _detect_help_request(content)
    closure_signal = _detect_closure_signal(content)
    repetition_signal = _detect_repetition_signal(content)
    current_covered_points = _infer_covered_points_from_text(
        content,
        has_concrete_actions=has_concrete_actions,
        episode_clarity=episode_clarity,
        problem_salience=problem_salience,
        reflection_phase=reflection_phase,
        closure_signal=closure_signal,
    )
    covered_points_set = set(previous_covered_points)
    covered_points_set.update(current_covered_points)
    covered_points = _ordered_point_list(covered_points_set, COVERED_POINT_ORDER)
    remaining_open_points = _compute_remaining_open_points(
        covered_points=covered_points_set,
        episode_clarity=episode_clarity,
        closure_signal=closure_signal,
        safety_or_quality_risk_level=safety_or_quality_risk_level,
    )
    loop_risk = _compute_loop_risk(
        repetition_signal=repetition_signal,
        last_tutorial_move=last_tutorial_move,
        consecutive_clarify_turns=consecutive_clarify_turns,
        previous_covered_points=previous_covered_points,
        current_covered_points=current_covered_points,
    )
    assistant_meta_leak_risk = _compute_assistant_meta_leak_risk(content)
    can_close_from_coverage = (
        "episode_described" in covered_points_set
        and bool(
            covered_points_set.intersection(
                {"cause_hypothesis_named", "cause_confirmed", "future_action_named", "learning_rule_named"}
            )
        )
    )
    structural_close = (
        session_phase == SESSION_PHASE_POTENTIAL_CLOSURE
        and session_maturity == "high"
        and evidence_strength == "high"
        and interaction_risk == "low"
        and cognitive_load != "high"
    )
    can_close_for_now = (
        (closure_signal == "explicit" and safety_or_quality_risk_level != "high")
        or structural_close
        or (
            can_close_from_coverage
            and interaction_risk != "high"
            and cognitive_load != "high"
        )
    )
    need_recap = (
        session_maturity == "high" and evidence_strength in {"medium", "high"}
    ) or (reflection_phase == "projection" and evidence_strength == "high")
    need_encouragement = self_efficacy_signal == "low" or affect_valence == "negative"
    need_reframing = (
        episode_clarity == "low"
        or (problem_salience == "none" and reflection_phase == "description")
        or repetition_signal != "none"
    )
    if closure_signal in {"implicit", "explicit"} or can_close_for_now:
        conversation_goal = "close_or_project"
    elif learner_help_request == "explicit":
        conversation_goal = "assist_reasoning"
    elif repetition_signal != "none":
        conversation_goal = "repair_or_shift"

    return TurnState(
        episode_clarity=episode_clarity,
        has_concrete_actions=has_concrete_actions,
        problem_salience=problem_salience,
        reflection_phase=reflection_phase,
        reflective_depth=reflective_depth,
        self_efficacy_signal=self_efficacy_signal,
        affect_valence=affect_valence,
        cognitive_load=cognitive_load,
        interaction_risk=interaction_risk,
        epistemic_balance=epistemic_balance,
        zpd_estimate=zpd_estimate,
        session_phase=session_phase,
        session_maturity=session_maturity,
        evidence_strength=evidence_strength,
        intervention_necessity=intervention_necessity,
        contradiction_status=contradiction_status,
        concept_clarity=concept_clarity,
        available_material=available_material,
        conversation_goal=conversation_goal,
        current_phase=session_phase,
        emotional_state=affect_valence,
        action_feasibility=action_feasibility,
        autonomy_level=autonomy_level,
        recent_progress=recent_progress,
        need_recap=need_recap,
        need_encouragement=need_encouragement,
        need_reframing=need_reframing,
        can_close_for_now=can_close_for_now,
        last_tutorial_move=last_tutorial_move,
        consecutive_clarify_turns=consecutive_clarify_turns,
        sticky_has_concrete_actions=has_concrete_actions and (sticky_session_actions or raw_has_concrete_actions),
        tech_representation_level=tech_representation_level,
        technical_criterion_focus=technical_criterion_focus,
        safety_or_quality_risk_level=safety_or_quality_risk_level,
        covered_points=covered_points,
        remaining_open_points=remaining_open_points,
        learner_help_request=learner_help_request,
        closure_signal=closure_signal,
        repetition_signal=repetition_signal,
        loop_risk=loop_risk,
        assistant_meta_leak_risk=assistant_meta_leak_risk,
        debug_signals=_debug_signal_payload(
            base_phase=base_phase,
            total_turns=total_turns,
            recent_traces=recent_traces,
            state_overrides=overrides,
            debug_overrides={
                "covered_points": covered_points,
                "remaining_open_points": remaining_open_points,
                "learner_help_request": learner_help_request,
                "closure_signal": closure_signal,
                "repetition_signal": repetition_signal,
                "loop_risk": loop_risk,
                "assistant_meta_leak_risk": assistant_meta_leak_risk,
                "can_close_from_coverage": can_close_from_coverage,
                "last_tutorial_move": last_tutorial_move,
                "consecutive_clarify_turns": consecutive_clarify_turns,
                "sticky_has_concrete_actions": has_concrete_actions and (sticky_session_actions or raw_has_concrete_actions),
                "tech_representation_level": tech_representation_level,
                "technical_criterion_focus": technical_criterion_focus,
                "safety_or_quality_risk_level": safety_or_quality_risk_level,
                **(debug_overrides or {}),
            },
        ),
    )
