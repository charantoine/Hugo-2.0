from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LearnerSpeechActResult:
    learner_speech_act: str
    last_learner_act: str
    requested_output: str = "none"
    confidence: float = 0.0
    reason_codes: list[str] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


HELP_PATTERNS = [
    r"\baide(?:\s|-)?moi\b",
    r"\btu peux m['’]aider\b",
    r"\btu m['’]aides a comprendre\b",
    r"\bpar quoi commencer\b",
    r"\bquoi verifier en premier\b",
    r"\bquoi vérifier en premier\b",
]
HOW_TO_PATTERNS = [
    r"\bcomment faire\b",
    r"\bcomment m['’]y prendre\b",
    r"\bcomment tu ferais\b",
]
RECAP_PATTERNS = [
    r"\b(fais|donne|propose)[ -]?(moi)?\s*(un )?(recap|récap|resume|résumé|bilan)\b",
    r"\bpeux[- ]tu me faire un (recap|récap|resume|résumé|bilan)\b",
]
REPORT_PATTERNS = [
    r"\btexte pour (le )?(tuteur|formateur)\b",
    r"\bcompte rendu pour (le )?(tuteur|formateur)\b",
    r"\brapport pour (le )?(tuteur|formateur)\b",
]
COMPETENCY_PATTERNS = [
    r"\bcompetences?\b",
    r"\bcompétences?\b",
    r"\bvue competences?\b",
    r"\bquelles competences\b",
    r"\bquelles compétences\b",
]
CLOSURE_PATTERNS = [
    r"\bon a fini\b",
    r"\bc['’]est fini\b",
    r"\bj['’]ai fini\b",
    r"\bon s['’]arrete\b",
    r"\bon s['’]arrête\b",
    r"\bon verra plus tard\b",
]
CONFUSION_PATTERNS = [
    r"\bje comprends pas\b",
    r"\bje ne comprends pas\b",
    r"\bje suis perdu\b",
    r"\bje vois pas\b",
    r"\bje bloque\b",
]
FATIGUE_PATTERNS = [
    r"\bj['’]en ai marre\b",
    r"\bje suis fatigue\b",
    r"\bje suis fatigu[ée]\b",
    r"\bca m['’]enerve\b",
    r"\bça m['’]énerve\b",
]
NEGOTIATE_PATTERNS = [
    r"\bon fait quoi maintenant\b",
    r"\bet ensuite\b",
    r"\bquelle suite\b",
    r"\bquelle prochaine etape\b",
    r"\bquelle prochaine étape\b",
]
REPETITION_PATTERNS = [
    r"\bon tourne en rond\b",
    r"\bdeja dit\b",
    r"\bdéjà dit\b",
    r"\bencore\b",
]


def classify_learner_speech_act(
    learner_message: str,
    recent_history: list[str] | None = None,
) -> LearnerSpeechActResult:
    text = str(learner_message or "").strip()
    history_text = " ".join(str(item or "") for item in (recent_history or [])[-3:])
    signals = {"history_hint": history_text[:240]}

    if _matches_any(text, REPORT_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="ask_report_for_tutor",
            last_learner_act="ask_report_for_tutor",
            requested_output="report_for_tutor",
            confidence=0.97,
            reason_codes=["explicit_report_request"],
            signals=signals,
        )
    if _matches_any(text, COMPETENCY_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="ask_competencies_view",
            last_learner_act="ask_competencies",
            requested_output="competencies_view",
            confidence=0.95,
            reason_codes=["explicit_competencies_request"],
            signals=signals,
        )
    if _matches_any(text, RECAP_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="ask_recap",
            last_learner_act="ask_recap",
            requested_output="recap",
            confidence=0.95,
            reason_codes=["explicit_recap_request"],
            signals=signals,
        )
    if _matches_any(text, CLOSURE_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="signal_closure",
            last_learner_act="signal_closure",
            requested_output="closure",
            confidence=0.94,
            reason_codes=["explicit_closure_request"],
            signals=signals,
        )
    if _matches_any(text, HELP_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="ask_help_diagnostic",
            last_learner_act="ask_help",
            requested_output="assist",
            confidence=0.93,
            reason_codes=["explicit_help_request"],
            signals=signals,
        )
    if _matches_any(text, HOW_TO_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="ask_how_to",
            last_learner_act="ask_priority",
            requested_output="assist",
            confidence=0.9,
            reason_codes=["explicit_how_to_request"],
            signals=signals,
        )
    if _matches_any(text, REPETITION_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="describe_situation",
            last_learner_act="signal_repetition",
            requested_output="none",
            confidence=0.88,
            reason_codes=["explicit_repetition_signal"],
            signals=signals,
        )
    if _matches_any(text, CONFUSION_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="express_confusion",
            last_learner_act="signal_confusion",
            requested_output="assist",
            confidence=0.84,
            reason_codes=["confusion_signal"],
            signals=signals,
        )
    if _matches_any(text, FATIGUE_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="express_tension_or_fatigue",
            last_learner_act="other",
            requested_output="assist",
            confidence=0.82,
            reason_codes=["fatigue_signal"],
            signals=signals,
        )
    if _matches_any(text, NEGOTIATE_PATTERNS):
        return LearnerSpeechActResult(
            learner_speech_act="negotiate_next_step",
            last_learner_act="negotiate_next_step",
            requested_output="reflect",
            confidence=0.8,
            reason_codes=["next_step_negotiation"],
            signals=signals,
        )
    return LearnerSpeechActResult(
        learner_speech_act="describe_situation",
        last_learner_act="none",
        requested_output="none",
        confidence=0.65,
        reason_codes=["default_describe_situation"],
        signals=signals,
    )
