from types import SimpleNamespace
from django.test import SimpleTestCase, override_settings

from apps.hugo.domain.schemas import ConversationDecision, TurnState
from apps.hugo.services.phase_decider import decide_next_phase, resolve_classifier_runtime_config


class PhaseDeciderTests(SimpleTestCase):
    def _session(
        self,
        backend: str = "ovh_ai",
        group_cfg: dict | None = None,
        session_cfg: dict | None = None,
    ):
        group_defaults = {
            "llm_backend": backend,
            "phase_classifier_enabled": None,
            "phase_classifier_max_tokens": None,
            "phase_classifier_min_confidence": None,
            "phase_classifier_max_input_chars": None,
        }
        if group_cfg:
            group_defaults.update(group_cfg)
        session_defaults = {
            "phase_classifier_enabled": None,
            "phase_classifier_max_tokens": None,
            "phase_classifier_min_confidence": None,
            "phase_classifier_max_input_chars": None,
        }
        if session_cfg:
            session_defaults.update(session_cfg)
        return SimpleNamespace(
            group=SimpleNamespace(**group_defaults),
            SessionPhase=SimpleNamespace(
                OPENING="opening",
                EXPLORATION="exploration",
                DEEPENING="deepening",
                POTENTIAL_CLOSURE="potential_closure",
            ),
            **session_defaults,
        )

    def _turn_state(self, **overrides):
        state = TurnState(
            episode_clarity="high",
            has_concrete_actions=True,
            problem_salience="low",
            reflection_phase="analysis",
            reflective_depth="high",
            self_efficacy_signal="neutral",
            affect_valence="neutral",
            cognitive_load="low",
            interaction_risk="low",
            epistemic_balance="balanced",
            zpd_estimate="in",
            session_phase="deepening",
            session_maturity="medium",
            evidence_strength="high",
            intervention_necessity="high",
            contradiction_status="none",
            concept_clarity="high",
            available_material="high",
            conversation_goal="deepen_analysis",
            current_phase="deepening",
            emotional_state="neutral",
            action_feasibility="high",
            autonomy_level="medium",
            recent_progress="steady",
            need_recap=False,
            need_encouragement=False,
            need_reframing=False,
            can_close_for_now=False,
        )
        for key, value in overrides.items():
            setattr(state, key, value)
        return state

    def _decision(self, **overrides):
        decision = ConversationDecision(
            primary_intent="deepen_analysis",
            pedagogical_move="analyze",
            number_of_questions=1,
            question_style="simple_open",
            should_explain_briefly=False,
            should_recap=False,
            should_encourage=False,
            should_reframe=False,
            should_close=False,
            response_constraints=["single_question_default"],
        )
        for key, value in overrides.items():
            setattr(decision, key, value)
        return decision

    def test_decider_uses_state_adapter_as_primary_phase_source(self):
        decision = decide_next_phase(
            session=self._session(session_cfg={"phase_classifier_enabled": False}),
            tutor_prompt=None,
            current_phase="exploration",
            user_input={"content": "J'ai decide parce que ..."},
            deterministic_next_phase="exploration",
            turn_state=self._turn_state(session_phase="exploration", current_phase="exploration"),
            conversation_decision=self._decision(),
        )
        self.assertEqual(decision.source, "state_adapter")
        self.assertEqual(decision.next_phase, "deepening")
        self.assertEqual(decision.reason, "decision_deepening")

    def test_decider_keeps_adapter_when_classifier_disabled(self):
        decision = decide_next_phase(
            session=self._session(session_cfg={"phase_classifier_enabled": False}),
            tutor_prompt=None,
            current_phase="exploration",
            user_input={"content": "Je ne sais pas trop"},
            deterministic_next_phase="exploration",
            turn_state=self._turn_state(session_phase="exploration", current_phase="exploration"),
            conversation_decision=self._decision(),
        )
        self.assertEqual(decision.source, "state_adapter")
        self.assertEqual(decision.next_phase, "deepening")
        self.assertEqual(decision.fallback_reason, "classifier_desactive")

    def test_decider_adapts_phase_back_to_exploration_for_clarification(self):
        decision = decide_next_phase(
            session=self._session(session_cfg={"phase_classifier_enabled": False}),
            tutor_prompt=None,
            current_phase="opening",
            user_input={"content": "texte"},
            deterministic_next_phase="exploration",
            turn_state=self._turn_state(
                session_phase="opening",
                current_phase="opening",
                episode_clarity="low",
                has_concrete_actions=False,
            ),
            conversation_decision=self._decision(pedagogical_move="clarify", primary_intent="clarify_episode"),
        )
        self.assertEqual(decision.source, "state_adapter")
        self.assertEqual(decision.next_phase, "exploration")
        self.assertEqual(decision.reason, "decision_exploration")

    def test_decider_uses_state_adapter_when_classifier_disabled(self):
        decision = decide_next_phase(
            session=self._session(session_cfg={"phase_classifier_enabled": False}),
            tutor_prompt=None,
            current_phase="deepening",
            user_input={"content": "texte"},
            deterministic_next_phase="deepening",
            turn_state=self._turn_state(can_close_for_now=True, session_phase="potential_closure", current_phase="potential_closure"),
            conversation_decision=self._decision(
                pedagogical_move="close",
                primary_intent="close_safely",
                should_close=True,
            ),
        )
        self.assertEqual(decision.source, "state_adapter")
        self.assertEqual(decision.next_phase, "potential_closure")
        self.assertEqual(decision.adapter_next_phase, "potential_closure")

    @override_settings(
        HUGO_PHASE_CLASSIFIER_ENABLED=True,
        HUGO_PHASE_CLASSIFIER_MAX_TOKENS=48,
        HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE=0.6,
        HUGO_PHASE_CLASSIFIER_MAX_INPUT_CHARS=700,
    )
    def test_runtime_resolver_uses_session_over_group_over_settings(self):
        session = self._session(
            group_cfg={
                "phase_classifier_enabled": False,
                "phase_classifier_max_tokens": 30,
                "phase_classifier_min_confidence": 0.55,
                "phase_classifier_max_input_chars": 650,
            },
            session_cfg={
                "phase_classifier_enabled": True,
                "phase_classifier_max_tokens": 22,
                "phase_classifier_min_confidence": 0.8,
                "phase_classifier_max_input_chars": 420,
            },
        )
        runtime_cfg, runtime_src = resolve_classifier_runtime_config(session)
        self.assertEqual(runtime_cfg["phase_classifier_enabled"], True)
        self.assertEqual(runtime_cfg["phase_classifier_max_tokens"], 22)
        self.assertEqual(runtime_cfg["phase_classifier_min_confidence"], 0.8)
        self.assertEqual(runtime_cfg["phase_classifier_max_input_chars"], 420)
        self.assertEqual(runtime_src["effective"], "session")

    @override_settings(
        HUGO_PHASE_CLASSIFIER_ENABLED=True,
        HUGO_PHASE_CLASSIFIER_MAX_TOKENS=48,
        HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE=0.6,
        HUGO_PHASE_CLASSIFIER_MAX_INPUT_CHARS=700,
    )
    def test_runtime_resolver_uses_group_when_session_not_set(self):
        session = self._session(
            group_cfg={
                "phase_classifier_enabled": False,
                "phase_classifier_max_tokens": 31,
                "phase_classifier_min_confidence": 0.51,
                "phase_classifier_max_input_chars": 620,
            },
        )
        runtime_cfg, runtime_src = resolve_classifier_runtime_config(session)
        self.assertEqual(runtime_cfg["phase_classifier_enabled"], False)
        self.assertEqual(runtime_cfg["phase_classifier_max_tokens"], 31)
        self.assertEqual(runtime_cfg["phase_classifier_min_confidence"], 0.51)
        self.assertEqual(runtime_cfg["phase_classifier_max_input_chars"], 620)
        self.assertEqual(runtime_src["effective"], "group")

    @override_settings(
        HUGO_PHASE_CLASSIFIER_ENABLED=False,
        HUGO_PHASE_CLASSIFIER_MAX_TOKENS=44,
        HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE=0.66,
        HUGO_PHASE_CLASSIFIER_MAX_INPUT_CHARS=710,
    )
    def test_runtime_resolver_uses_settings_fallback(self):
        session = self._session()
        runtime_cfg, runtime_src = resolve_classifier_runtime_config(session)
        self.assertEqual(runtime_cfg["phase_classifier_enabled"], False)
        self.assertEqual(runtime_cfg["phase_classifier_max_tokens"], 44)
        self.assertEqual(runtime_cfg["phase_classifier_min_confidence"], 0.66)
        self.assertEqual(runtime_cfg["phase_classifier_max_input_chars"], 710)
        self.assertEqual(runtime_src["effective"], "settings")
