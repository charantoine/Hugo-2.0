from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import List, Dict, Any, Optional


SESSION_PHASE_OPENING = "opening"
SESSION_PHASE_EXPLORATION = "exploration"
SESSION_PHASE_DEEPENING = "deepening"
SESSION_PHASE_POTENTIAL_CLOSURE = "potential_closure"
SESSION_PHASE_ALIASES = {
    "conceptualization": SESSION_PHASE_DEEPENING,
    "closure": SESSION_PHASE_POTENTIAL_CLOSURE,
}
SESSION_PHASE_VALUES = {
    SESSION_PHASE_OPENING,
    SESSION_PHASE_EXPLORATION,
    SESSION_PHASE_DEEPENING,
    SESSION_PHASE_POTENTIAL_CLOSURE,
}
CONVERSATION_PROFILE_DIAGNOSTIC = "diagnostic"
CONVERSATION_PROFILE_REFLECTIVE_AFEST = "reflective_afest"
CONVERSATION_PROFILE_KNOWLEDGE_REVIEW = "knowledge_review"
CONVERSATION_PROFILE_VALUES = {
    CONVERSATION_PROFILE_DIAGNOSTIC,
    CONVERSATION_PROFILE_REFLECTIVE_AFEST,
    CONVERSATION_PROFILE_KNOWLEDGE_REVIEW,
}
P0_CORE_FIELDS = [
    "has_concrete_actions",
    "episode_clarity",
    "problem_salience",
    "reflection_phase",
    "affect_valence",
    "cognitive_load",
    "interaction_risk",
    "session_phase",
]
P0_LLM_FIELDS = [
    "has_concrete_actions",
    "episode_clarity",
    "problem_salience",
    "reflection_phase",
    "affect_valence",
    "cognitive_load",
    "interaction_risk",
]


def normalize_session_phase(value: Any, default: str = SESSION_PHASE_EXPLORATION) -> str:
    phase = str(value or "").strip().lower()
    if not phase:
        return default
    phase = SESSION_PHASE_ALIASES.get(phase, phase)
    return phase if phase in SESSION_PHASE_VALUES else default


def normalize_conversation_profile(
    value: Any,
    default: str = CONVERSATION_PROFILE_REFLECTIVE_AFEST,
) -> str:
    profile = str(value or "").strip().lower()
    if not profile:
        return default
    return profile if profile in CONVERSATION_PROFILE_VALUES else default


@dataclass
class LearnerStateSlice:
    learner_id: str
    group_id: Optional[str]
    focus_candidates: List[Dict[str, Any]] = field(default_factory=list)
    open_action_items: List[Dict[str, Any]] = field(default_factory=list)
    signals: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningStage:
    group_id: str
    item_id: str
    stage: str
    expected_level_now: str
    final_target_level: str
    priority: str
    intermediate_objective_label: str
    intermediate_objective_window_from: Optional[date] = None
    intermediate_objective_window_to: Optional[date] = None


@dataclass
class PedagogicalProfile:
    group_id: str
    item_id: str
    focus_weights: Dict[str, float]
    directive_level: str
    risk_sensitivity: str
    coach_questions_typed: List[Dict[str, Any]] = field(default_factory=list)
    critical_mistakes: List[str] = field(default_factory=list)
    exemplar_situations: List[str] = field(default_factory=list)


@dataclass
class CompetenceBrief:
    item_id: str
    label: str
    key_criteria: List[str]
    expected_evidence: List[str]
    critical_mistakes: List[str]
    typical_situations: List[str]
    preferred_coach_questions: List[str]


@dataclass
class TeachingPlan:
    conversation_profile: str
    session_phase: str
    focus_competence: Dict[str, Any]
    learning_stage: str
    expected_level_now: str
    current_level: str
    coverage_status: str
    regulation_targets: Dict[str, float]
    open_action_items: List[str]
    critical_mistakes: List[str]
    coach_questions_candidates: List[str]
    rag_mode: str
    ui_focus_label: str
    max_questions_this_turn: int
    next_session_phase: Optional[str] = None
    primary_intent: str = ""
    pedagogical_move: str = ""
    question_style: str = "simple_open"
    should_recap: bool = False
    should_encourage: bool = False
    should_reframe: bool = False
    should_close: bool = False
    response_constraints: List[str] = field(default_factory=list)
    phase_source: str = "state_adapter"


@dataclass
class TurnState:
    episode_clarity: str
    has_concrete_actions: bool
    problem_salience: str
    reflection_phase: str
    reflective_depth: str
    self_efficacy_signal: str
    affect_valence: str
    cognitive_load: str
    interaction_risk: str
    epistemic_balance: str
    zpd_estimate: str
    session_phase: str
    session_maturity: str
    evidence_strength: str
    intervention_necessity: str
    contradiction_status: str
    concept_clarity: str
    available_material: str
    conversation_goal: str
    current_phase: str
    emotional_state: str
    action_feasibility: str
    autonomy_level: str
    recent_progress: str
    need_recap: bool
    need_encouragement: bool
    need_reframing: bool
    can_close_for_now: bool
    last_tutorial_move: str = ""
    consecutive_clarify_turns: int = 0
    sticky_has_concrete_actions: bool = False
    tech_representation_level: str = "implicit"
    technical_criterion_focus: str = "none"
    safety_or_quality_risk_level: str = "low"
    covered_points: List[str] = field(default_factory=list)
    remaining_open_points: List[str] = field(default_factory=list)
    learner_help_request: str = "none"
    closure_signal: str = "none"
    repetition_signal: str = "none"
    loop_risk: str = "low"
    assistant_meta_leak_risk: str = "low"
    debug_signals: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["p0"] = {
            key: payload[key]
            for key in P0_CORE_FIELDS
        }
        return payload


@dataclass
class ConversationDecision:
    primary_intent: str
    pedagogical_move: str
    number_of_questions: int
    question_style: str
    should_explain_briefly: bool
    should_recap: bool
    should_encourage: bool
    should_reframe: bool
    should_close: bool
    response_constraints: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConversationProgress:
    conversation_profile: str
    branch_key: str
    branch_label: str
    active_objective: str
    stage_index: int
    current_step_id: str
    current_step_label: str
    percent: int
    maturity: str
    can_summarize: bool
    evaluation_eligible: bool
    closure_eligible: bool
    rag_allowed: bool
    supported_by_documents: bool
    covered_points: List[str] = field(default_factory=list)
    remaining_open_points: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)
    next_recommended_action: str = ""
    tutor_signal_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


SESSION_MEMORY_SCOPE_INTRA_CONVERSATION = "intra_conversation"


@dataclass
class SessionMemoryContract:
    session_id: str
    updated_at: str
    theme: str = ""
    learning_objective: str = ""
    facts_confirmed: List[str] = field(default_factory=list)
    open_points: List[str] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)
    memory_scope: str = SESSION_MEMORY_SCOPE_INTRA_CONVERSATION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemorySummaryResponse:
    session_memory: Dict[str, Any]
    theme_memories: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SessionMemorySummary:
    summary: str
    active_themes: List[str] = field(default_factory=list)
    carry_over_points: List[str] = field(default_factory=list)
    open_action_items: List[str] = field(default_factory=list)
    last_session_at: Optional[str] = None
    sessions_considered: int = 0
    validated_traces_count: int = 0
    memory_scope: str = "governed_structured"
    contract: Optional[SessionMemoryContract] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "summary": self.summary,
            "active_themes": list(self.active_themes),
            "carry_over_points": list(self.carry_over_points),
            "open_action_items": list(self.open_action_items),
            "last_session_at": self.last_session_at,
            "sessions_considered": self.sessions_considered,
            "validated_traces_count": self.validated_traces_count,
            "memory_scope": self.memory_scope,
        }
        if self.contract is not None:
            payload["session_memory"] = self.contract.to_dict()
        return payload


@dataclass
class UiState:
    header_badges: List[Dict[str, Any]] = field(default_factory=list)
    scene_progress: Dict[str, Any] = field(default_factory=dict)
    quest_cards: List[Dict[str, Any]] = field(default_factory=list)
    persistent_objects: List[Dict[str, Any]] = field(default_factory=list)
    symbolic_rewards: List[Dict[str, Any]] = field(default_factory=list)
    supporting_documents: List[Dict[str, Any]] = field(default_factory=list)
    session_memory: Dict[str, Any] = field(default_factory=dict)
    tutor_signals: Dict[str, Any] = field(default_factory=dict)
    ui_visibility_flags: Dict[str, Any] = field(default_factory=dict)
    gamification_profile: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class P0ClassifierResult:
    turn_state: TurnState
    source: str
    confidence: float = 0.0
    fallback_reason: str = ""
    classifier_provider: str = ""
    classifier_model: str = ""
    runtime_config: Dict[str, Any] = field(default_factory=dict)
    runtime_config_source: Dict[str, Any] = field(default_factory=dict)
    source_by_field: Dict[str, Any] = field(default_factory=dict)
    llm_meta: Dict[str, Any] = field(default_factory=dict)
    system_prompt: str = ""
    user_prompt: str = ""
    classifier_reply_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        preview = (self.classifier_reply_text or "")[:4000]
        return {
            "source": self.source,
            "confidence": self.confidence,
            "fallback_reason": self.fallback_reason,
            "classifier_provider": self.classifier_provider,
            "classifier_model": self.classifier_model,
            "runtime_config": self.runtime_config,
            "runtime_config_source": self.runtime_config_source,
            "source_by_field": self.source_by_field,
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "classifier_reply_text": preview,
            "request_payload": self.llm_meta.get("request_payload"),
            "raw_response": self.llm_meta.get("raw_response"),
            "llm_error": self.llm_meta.get("error", ""),
        }

