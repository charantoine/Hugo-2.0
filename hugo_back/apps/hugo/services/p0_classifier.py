from __future__ import annotations

import json
import re
from typing import Any

from django.conf import settings

from apps.hugo.domain.schemas import P0_LLM_FIELDS, P0ClassifierResult, TurnState
from apps.hugo.llm_client import complete_with_provider
from apps.hugo.models import HugoSession, TutorPrompt
from apps.hugo.services.turn_state_analyzer import analyze_turn_state

P0_CLASSIFIER_PRESETS = {
    "safe": {
        "p0_classifier_enabled": True,
        "p0_classifier_min_confidence": 0.75,
        "p0_classifier_max_tokens": 120,
        "p0_classifier_max_input_chars": 700,
    },
    "balanced": {
        "p0_classifier_enabled": True,
        "p0_classifier_min_confidence": 0.60,
        "p0_classifier_max_tokens": 180,
        "p0_classifier_max_input_chars": 900,
    },
    "aggressive": {
        "p0_classifier_enabled": True,
        "p0_classifier_min_confidence": 0.45,
        "p0_classifier_max_tokens": 240,
        "p0_classifier_max_input_chars": 1200,
    },
}

P0_ALLOWED_VALUES: dict[str, set[Any]] = {
    "has_concrete_actions": {True, False},
    "episode_clarity": {"low", "medium", "high"},
    "problem_salience": {"none", "low", "high"},
    "reflection_phase": {"description", "analysis", "projection"},
    "affect_valence": {"negative", "neutral", "positive"},
    "cognitive_load": {"low", "medium", "high"},
    "interaction_risk": {"low", "medium", "high"},
}


def _resolve_provider(session: HugoSession) -> str:
    group = getattr(session, "group", None)
    if group and getattr(group, "llm_backend", None):
        return str(group.llm_backend).lower()
    return str(getattr(settings, "LLM_PROVIDER_DEFAULT", "ollama")).lower()


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default
    return parsed if parsed > 0 else default


def _coerce_confidence(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        return default
    if parsed < 0 or parsed > 1:
        return default
    return parsed


def _pick_cascade_value(
    session: HugoSession,
    field_name: str,
    setting_name: str,
    setting_default: Any,
) -> tuple[Any, str]:
    session_value = getattr(session, field_name, None)
    if session_value is not None:
        return session_value, "session"
    group = getattr(session, "group", None)
    group_value = getattr(group, field_name, None) if group else None
    if group_value is not None:
        return group_value, "group"
    return getattr(settings, setting_name, setting_default), "settings"


def resolve_p0_classifier_runtime_config(session: HugoSession) -> tuple[dict[str, Any], dict[str, Any]]:
    enabled_raw, enabled_src = _pick_cascade_value(
        session,
        "p0_classifier_enabled",
        "HUGO_P0_CLASSIFIER_ENABLED",
        P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_enabled"],
    )
    max_tokens_raw, max_tokens_src = _pick_cascade_value(
        session,
        "p0_classifier_max_tokens",
        "HUGO_P0_CLASSIFIER_MAX_TOKENS",
        P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_max_tokens"],
    )
    min_conf_raw, min_conf_src = _pick_cascade_value(
        session,
        "p0_classifier_min_confidence",
        "HUGO_P0_CLASSIFIER_MIN_CONFIDENCE",
        P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_min_confidence"],
    )
    max_input_chars_raw, max_input_chars_src = _pick_cascade_value(
        session,
        "p0_classifier_max_input_chars",
        "HUGO_P0_CLASSIFIER_MAX_INPUT_CHARS",
        P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_max_input_chars"],
    )
    runtime_config = {
        "p0_classifier_enabled": bool(enabled_raw),
        "p0_classifier_max_tokens": _coerce_positive_int(
            max_tokens_raw,
            P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_max_tokens"],
        ),
        "p0_classifier_min_confidence": _coerce_confidence(
            min_conf_raw,
            P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_min_confidence"],
        ),
        "p0_classifier_max_input_chars": _coerce_positive_int(
            max_input_chars_raw,
            P0_CLASSIFIER_PRESETS["balanced"]["p0_classifier_max_input_chars"],
        ),
    }
    source_by_field = {
        "p0_classifier_enabled": enabled_src,
        "p0_classifier_max_tokens": max_tokens_src,
        "p0_classifier_min_confidence": min_conf_src,
        "p0_classifier_max_input_chars": max_input_chars_src,
    }
    unique_sources = {src for src in source_by_field.values()}
    source_by_field["effective"] = unique_sources.pop() if len(unique_sources) == 1 else "mixed"
    return runtime_config, source_by_field


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """
    Extrait le premier objet JSON du texte modèle (préambule, blocs ```json```,
    JSON tronqué partiellement évités autant que possible via raw_decode).
    """
    body = (text or "").strip()
    if not body:
        return None
    # Remplacer guillemets typographiques courants (copier-coller / modèles)
    body = (
        body.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u00ab", '"')
        .replace("\u00bb", '"')
    )
    candidates: list[str] = []
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", body, flags=re.IGNORECASE)
    if fence:
        candidates.append(fence.group(1).strip())
    candidates.append(body)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        start = candidate.find("{")
        if start < 0:
            continue
        try:
            obj, _ = decoder.raw_decode(candidate, start)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    try:
        parsed = json.loads(body)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    match = re.search(r"\{[\s\S]*\}", body)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    raw = str(value or "").strip().lower()
    if raw in {"true", "1", "yes", "oui"}:
        return True
    if raw in {"false", "0", "no", "non"}:
        return False
    return None


def _normalize_llm_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    normalized: dict[str, Any] = {}
    for field_name in P0_LLM_FIELDS:
        if field_name not in payload:
            return None
        raw_value = payload.get(field_name)
        if field_name == "has_concrete_actions":
            parsed_bool = _normalize_bool(raw_value)
            if parsed_bool is None:
                return None
            normalized[field_name] = parsed_bool
            continue
        value = str(raw_value or "").strip().lower()
        if value not in P0_ALLOWED_VALUES[field_name]:
            return None
        normalized[field_name] = value
    return normalized


def _build_classifier_context(ctx: Any) -> str:
    parts: list[str] = []
    learner_summary = str(getattr(ctx, "learner_summary", "") or "").strip()
    if learner_summary:
        parts.append(f"- resume_apprenant: {learner_summary[:280]}")
    recent_traces = list(getattr(ctx, "recent_traces_info", []) or [])
    if recent_traces:
        compact_traces = [str(item)[:140] for item in recent_traces[:2]]
        parts.append(f"- traces_recentes: {' | '.join(compact_traces)}")
    class_documents = list(getattr(ctx, "class_documents", []) or [])
    if class_documents:
        compact_docs = [str(item)[:80] for item in class_documents[:3]]
        parts.append(f"- documents_classe: {' | '.join(compact_docs)}")
    return "\n".join(parts) if parts else "- aucun_contexte_supplementaire"


def _build_classifier_prompts(
    *,
    session: HugoSession,
    user_input: dict[str, Any],
    ctx: Any,
    heuristic_state: TurnState,
    max_input_chars: int,
) -> tuple[str, str]:
    learner_message = str(user_input.get("content") or "").strip()[:max_input_chars]
    system_prompt = (
        "Tu es un classifieur P0 Hugo 1.6.2. "
        "Reponds UNIQUEMENT avec un seul objet JSON valide (pas de markdown, pas de ```, pas de texte avant ou apres). "
        "Cles en anglais, guillemets doubles, booleens true/false en minuscules, nombres avec point decimal. "
        "Evalue seulement les variables demandees. "
        'Format attendu: {"confidence":0.0,"episode_clarity":"low|medium|high",'
        '"has_concrete_actions":true,"problem_salience":"none|low|high",'
        '"reflection_phase":"description|analysis|projection",'
        '"affect_valence":"negative|neutral|positive",'
        '"cognitive_load":"low|medium|high",'
        '"interaction_risk":"low|medium|high"}.'
    )
    user_prompt = (
        f'phase_session="{heuristic_state.session_phase}"\n'
        f'heuristique_reference={json.dumps({key: getattr(heuristic_state, key) for key in P0_LLM_FIELDS}, ensure_ascii=True)}\n'
        f'contexte={_build_classifier_context(ctx)}\n'
        f'dernier_message_apprenant="{learner_message}"\n'
        "Retourne un JSON strict et complet."
    )
    return system_prompt, user_prompt


def classify_p0_turn_state(
    *,
    session: HugoSession,
    tutor_prompt: TutorPrompt | None,
    user_input: dict[str, Any],
    ctx: Any,
    heuristic_state: TurnState,
) -> P0ClassifierResult:
    runtime_config, runtime_config_source = resolve_p0_classifier_runtime_config(session)
    provider = _resolve_provider(session)
    if not bool(runtime_config["p0_classifier_enabled"]):
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            fallback_reason="classifier_desactive",
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
        )

    learner_content = str(user_input.get("content") or "").strip()
    if not learner_content:
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            fallback_reason="input_vide",
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
        )

    system_prompt, user_prompt = _build_classifier_prompts(
        session=session,
        user_input=user_input,
        ctx=ctx,
        heuristic_state=heuristic_state,
        max_input_chars=int(runtime_config["p0_classifier_max_input_chars"]),
    )
    text, llm_meta = complete_with_provider(
        prompt=user_prompt,
        system=system_prompt,
        max_tokens=int(runtime_config["p0_classifier_max_tokens"]),
        provider=provider,
        tutor_prompt=tutor_prompt,
    )
    text = (text or "").strip()
    llm_err = str(llm_meta.get("error") or "").strip()
    if llm_err:
        base_result = {
            "runtime_config": runtime_config,
            "runtime_config_source": runtime_config_source,
            "classifier_provider": provider,
            "classifier_model": str(llm_meta.get("model_used") or ""),
            "llm_meta": llm_meta,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            confidence=0.0,
            fallback_reason="llm_indisponible",
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
            classifier_reply_text=text,
            **base_result,
        )
    if not text:
        base_result = {
            "runtime_config": runtime_config,
            "runtime_config_source": runtime_config_source,
            "classifier_provider": provider,
            "classifier_model": str(llm_meta.get("model_used") or ""),
            "llm_meta": llm_meta,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            confidence=0.0,
            fallback_reason="reponse_vide",
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
            classifier_reply_text="",
            **base_result,
        )
    parsed = _extract_json_object(text)
    confidence = _coerce_confidence((parsed or {}).get("confidence"), 0.0)
    base_result = {
        "runtime_config": runtime_config,
        "runtime_config_source": runtime_config_source,
        "classifier_provider": provider,
        "classifier_model": str(llm_meta.get("model_used") or ""),
        "llm_meta": llm_meta,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "classifier_reply_text": text,
    }
    if not parsed:
        fb = "parse_invalide"
        if text and "{" in text and not text.rstrip().endswith("}"):
            fb = "parse_invalide_reponse_probablement_tronquee"
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            confidence=confidence,
            fallback_reason=fb,
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
            **base_result,
        )
    normalized_payload = _normalize_llm_payload(parsed)
    if not normalized_payload:
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            confidence=confidence,
            fallback_reason="payload_invalide",
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
            **base_result,
        )
    min_confidence = float(runtime_config["p0_classifier_min_confidence"])
    if confidence < min_confidence:
        return P0ClassifierResult(
            turn_state=heuristic_state,
            source="heuristic",
            confidence=confidence,
            fallback_reason="confiance_trop_faible",
            source_by_field={field_name: "heuristic" for field_name in P0_LLM_FIELDS},
            **base_result,
        )

    merged_state = analyze_turn_state(
        session=session,
        user_input=user_input,
        ctx=ctx,
        state_overrides=normalized_payload,
        debug_overrides={
            "p0_classifier_source": "llm_classifier",
            "p0_classifier_confidence": confidence,
        },
    )
    source_by_field = {field_name: "heuristic" for field_name in merged_state.to_dict()["p0"].keys()}
    for field_name in normalized_payload:
        source_by_field[field_name] = "llm_classifier"
    return P0ClassifierResult(
        turn_state=merged_state,
        source="llm_classifier",
        confidence=confidence,
        source_by_field=source_by_field,
        **base_result,
    )
