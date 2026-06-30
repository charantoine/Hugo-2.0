from __future__ import annotations

import re

from apps.hugo.domain.conversation_decision_v17 import ConversationDecisionV17
from apps.hugo.services.prompt_renderer_v17 import TutorPromptProfile


def _compact_sentence(text: str, max_chars: int = 260) -> str:
    clean = " ".join((text or "").split()).strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3].rstrip() + "..."


def _strip_lists(text: str) -> str:
    lines = []
    for raw in (text or "").splitlines():
        line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", raw).strip()
        if line:
            lines.append(line)
    return " ".join(lines).strip()


def _extract_questions(text: str) -> list[str]:
    return [_compact_sentence(q.strip()) for q in re.findall(r"[^?!\n]*\?+", text or "") if q.strip()]


def _non_question_text(text: str) -> str:
    stripped = re.sub(r"[^.?!\n]*\?+", "", text or "")
    stripped = _strip_lists(stripped)
    return _compact_sentence(stripped)


def _is_blocked(question: str, blocked_topics: list[str]) -> bool:
    clean = " ".join((question or "").lower().split())
    return any(topic and topic.lower() in clean for topic in blocked_topics)


def apply_output_guardrails_v17(
    raw_response: str,
    decision: ConversationDecisionV17,
    profile: TutorPromptProfile,
) -> str:
    target = max(0, min(int(decision.target_question_count or 0), 2))
    blocked_topics = list(decision.blocked_question_topics or [])
    text = str(raw_response or "").strip()
    if not text:
        if decision.response_mode == "closure":
            return "D'accord, on peut s'arrêter ici."
        if decision.response_mode == "assist":
            return "Je t'aide brièvement à partir de ce que tu as déjà observé."
        return ""

    if decision.response_mode in {"recap", "evaluation", "closure"} or target == 0:
        summary = _non_question_text(text)
        if summary:
            return summary
        if decision.response_mode == "closure":
            return "D'accord, on peut s'arrêter ici."
        if decision.response_mode == "evaluation":
            return "Voici un mini-bilan prudent de ce qui semble acquis."
        return "Voici l'essentiel en bref."

    questions = [q for q in _extract_questions(text) if not _is_blocked(q, blocked_topics)]
    questions = questions[:target]
    prefix = _non_question_text(text)

    if decision.response_mode == "assist":
        if target <= 0 or not questions:
            return prefix or "Je t'aide brièvement à partir du dernier fait concret."
        if prefix:
            return f"{prefix}\n1. {questions[0]}"
        return f"1. {questions[0]}"

    if not questions:
        return prefix or _compact_sentence(text)

    if prefix:
        return prefix + "\n" + "\n".join(f"{idx + 1}. {question}" for idx, question in enumerate(questions))
    return "\n".join(f"{idx + 1}. {question}" for idx, question in enumerate(questions))
