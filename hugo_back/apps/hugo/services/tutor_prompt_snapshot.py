"""Serialize TutorPrompt state at turn time for audit and reproducibility."""
from __future__ import annotations

from typing import Any

from apps.hugo.models import TutorPrompt


def build_tutor_prompt_snapshot(tp: TutorPrompt | None) -> dict[str, Any]:
    """Return a JSON-serializable dict of the prompt as used for this turn."""
    if tp is None:
        return {}
    ovh = getattr(tp, "ovh_llm", None)
    ovh_payload = None
    if ovh is not None:
        ovh_payload = {"id": str(ovh.id), "code": ovh.code}
    return {
        "id": str(tp.id),
        "code": tp.code,
        "name": tp.name,
        "prompt_type": tp.prompt_type,
        "updated_at": tp.updated_at.isoformat() if tp.updated_at else None,
        "output_format_mode": tp.output_format_mode,
        "max_questions_per_turn": tp.max_questions_per_turn,
        "max_tokens": tp.max_tokens,
        "default_session_phase": tp.default_session_phase or "",
        "tone": tp.tone,
        "language": tp.language,
        "allow_lists": tp.allow_lists,
        "regulation_bias_task": tp.regulation_bias_task,
        "regulation_bias_reasoning": tp.regulation_bias_reasoning,
        "regulation_bias_metacognition": tp.regulation_bias_metacognition,
        "sot_profile": tp.sot_profile or "",
        "ovh_llm": ovh_payload,
        "system_template": tp.system_template,
        "user_template": tp.user_template,
        "metadata": tp.metadata or {},
    }
