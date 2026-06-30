from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from apps.hugo.domain.schemas import ConversationDecision


@dataclass
class ConversationDecisionV17:
    primary_intent: str
    pedagogical_move: str
    response_mode: str
    target_question_count: int
    number_of_questions: int
    question_style: str = "simple_open"
    question_bundling_allowed: bool = False
    micro_explanation_allowed: bool = False
    should_explain_briefly: bool = False
    should_recap: bool = False
    should_encourage: bool = False
    should_reframe: bool = False
    should_close: bool = False
    should_acknowledge_repetition: bool = False
    should_acknowledge_closure: bool = False
    blocked_question_topics: List[str] = field(default_factory=list)
    response_constraints: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    effective_max_questions_this_turn: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def from_legacy_conversation_decision(decision: ConversationDecision) -> ConversationDecisionV17:
    response_mode = "reflect"
    if decision.pedagogical_move == "assist":
        response_mode = "assist"
    elif decision.pedagogical_move == "close" or decision.should_close or decision.number_of_questions == 0:
        response_mode = "closure"
    metadata = dict(decision.metadata or {})
    return ConversationDecisionV17(
        primary_intent=decision.primary_intent,
        pedagogical_move=decision.pedagogical_move,
        response_mode=response_mode,
        target_question_count=decision.number_of_questions,
        number_of_questions=decision.number_of_questions,
        question_style=decision.question_style,
        question_bundling_allowed=decision.number_of_questions > 1,
        micro_explanation_allowed=decision.should_explain_briefly,
        should_explain_briefly=decision.should_explain_briefly,
        should_recap=decision.should_recap,
        should_encourage=decision.should_encourage,
        should_reframe=decision.should_reframe,
        should_close=decision.should_close,
        should_acknowledge_repetition=metadata.get("repetition_signal") == "explicit",
        should_acknowledge_closure=metadata.get("closure_signal") == "explicit",
        blocked_question_topics=list(metadata.get("covered_points") or []),
        response_constraints=list(decision.response_constraints or []),
        reason_codes=list(decision.reason_codes or []),
        metadata={**metadata, "legacy_snapshot": decision.to_dict(), "contract_version": "1.7"},
        effective_max_questions_this_turn=decision.number_of_questions,
    )


def to_legacy_conversation_decision(decision: ConversationDecisionV17) -> ConversationDecision:
    snapshot = dict(decision.metadata.get("legacy_snapshot") or {})
    base = {
        "primary_intent": decision.primary_intent,
        "pedagogical_move": decision.pedagogical_move,
        "number_of_questions": decision.target_question_count,
        "question_style": "no_question" if decision.target_question_count <= 0 else ("double_same_goal" if decision.target_question_count >= 2 else "simple_open"),
        "should_explain_briefly": decision.should_explain_briefly,
        "should_recap": decision.should_recap,
        "should_encourage": decision.should_encourage,
        "should_reframe": decision.should_reframe,
        "should_close": decision.should_close,
        "response_constraints": [],
        "reason_codes": [],
        "metadata": {},
    }
    for key, value in snapshot.items():
        if key in base:
            base[key] = value
    merged_constraints = list(base.get("response_constraints") or [])
    merged_constraints.extend(list(decision.response_constraints or []))
    merged_constraints.extend(
        [
            f"response_mode:{decision.response_mode}",
            f"target_question_count:{decision.target_question_count}",
        ]
    )
    if decision.blocked_question_topics:
        merged_constraints.append("blocked_topics_present")
    question_style = decision.question_style or base["question_style"]
    if decision.target_question_count <= 0:
        question_style = "no_question"
    elif decision.target_question_count >= 2 and question_style == "simple_open":
        question_style = "double_same_goal"
    metadata = {
        **dict(base.get("metadata") or {}),
        **dict(decision.metadata or {}),
        "contract_version": "1.7",
        "response_mode": decision.response_mode,
        "target_question_count": decision.target_question_count,
        "effective_max_questions_this_turn": decision.effective_max_questions_this_turn or decision.target_question_count,
        "blocked_question_topics": list(decision.blocked_question_topics or []),
    }
    return ConversationDecision(
        primary_intent=decision.primary_intent,
        pedagogical_move=decision.pedagogical_move,
        number_of_questions=max(0, decision.target_question_count),
        question_style=question_style,
        should_explain_briefly=decision.should_explain_briefly,
        should_recap=decision.should_recap,
        should_encourage=decision.should_encourage,
        should_reframe=decision.should_reframe,
        should_close=decision.should_close,
        response_constraints=merged_constraints,
        reason_codes=list(dict.fromkeys(list(base.get("reason_codes") or []) + list(decision.reason_codes or []))),
        metadata=metadata,
    )
