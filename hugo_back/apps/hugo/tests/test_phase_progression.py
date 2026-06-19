from types import SimpleNamespace
from uuid import uuid4

from django.test import SimpleTestCase

from apps.hugo.domain.schemas import ConversationDecision, LearnerStateSlice, LearningStage, PedagogicalProfile, TurnState
from apps.hugo.services.hugo_orchestrator import _resolve_effective_phase
from apps.hugo.services.teaching_plan_builder import (
    build_teaching_plan,
    compute_next_session_phase,
)


class PhaseResolutionTests(SimpleTestCase):
    def test_resolve_effective_phase_priority_request_first(self):
        session = SimpleNamespace(
            manual_phase_override="deepening",
            current_phase="exploration",
            SessionPhase=SimpleNamespace(EXPLORATION="exploration"),
        )
        phase = _resolve_effective_phase(session, {"session_phase": "potential_closure"})
        self.assertEqual(phase, "potential_closure")

    def test_resolve_effective_phase_uses_manual_then_current(self):
        session = SimpleNamespace(
            manual_phase_override="opening",
            current_phase="deepening",
            SessionPhase=SimpleNamespace(EXPLORATION="exploration"),
        )
        phase = _resolve_effective_phase(session, {})
        self.assertEqual(phase, "opening")

        session.manual_phase_override = None
        phase = _resolve_effective_phase(session, {})
        self.assertEqual(phase, "deepening")


class PhaseTransitionTests(SimpleTestCase):
    def test_compute_next_phase_progression_rules(self):
        self.assertEqual(
            compute_next_session_phase("opening", {"content": "J'interviens sur une panne"}),
            "exploration",
        )
        self.assertEqual(
            compute_next_session_phase("exploration", {"content": "J'ai choisi ce test parce que c'etait le plus fiable"}),
            "deepening",
        )
        self.assertEqual(
            compute_next_session_phase("deepening", {"content": "Prochaine fois je vais suivre cette checklist"}),
            "potential_closure",
        )
        self.assertEqual(
            compute_next_session_phase("potential_closure", {"content": "On cloture"}),
            "potential_closure",
        )

    def test_build_teaching_plan_sets_session_and_next_phase(self):
        learner_slice = LearnerStateSlice(
            learner_id=str(uuid4()),
            group_id=str(uuid4()),
            focus_candidates=[],
            open_action_items=[],
            signals={},
        )
        learning_stage = LearningStage(
            group_id=str(uuid4()),
            item_id="",
            stage="intermediate",
            expected_level_now="participe",
            final_target_level="maitrise",
            priority="medium",
            intermediate_objective_label="",
        )
        pedagogical_profile = PedagogicalProfile(
            group_id=str(uuid4()),
            item_id="",
            focus_weights={"task": 0.3, "reasoning": 0.5, "metacognition": 0.2},
            directive_level="balanced",
            risk_sensitivity="normal",
        )

        plan = build_teaching_plan(
            learner_slice=learner_slice,
            learning_stage=learning_stage,
            pedagogical_profile=pedagogical_profile,
            user_input={
                "session_phase": "exploration",
                "content": "J'ai decide de prioriser ce controle parce que le risque etait eleve",
            },
            max_questions_per_turn=2,
        )

        self.assertEqual(plan.session_phase, "exploration")
        self.assertEqual(plan.next_session_phase, "deepening")

    def test_build_teaching_plan_consumes_turn_state_and_decision(self):
        learner_slice = LearnerStateSlice(
            learner_id=str(uuid4()),
            group_id=str(uuid4()),
            focus_candidates=[],
            open_action_items=[{"label": "Verifier l'ordre des actions"}],
            signals={},
        )
        learning_stage = LearningStage(
            group_id=str(uuid4()),
            item_id="",
            stage="intermediate",
            expected_level_now="participe",
            final_target_level="maitrise",
            priority="medium",
            intermediate_objective_label="",
        )
        pedagogical_profile = PedagogicalProfile(
            group_id=str(uuid4()),
            item_id="",
            focus_weights={"task": 0.3, "reasoning": 0.5, "metacognition": 0.2},
            directive_level="balanced",
            risk_sensitivity="normal",
        )
        turn_state = TurnState(
            episode_clarity="medium",
            has_concrete_actions=False,
            problem_salience="low",
            reflection_phase="description",
            reflective_depth="low",
            self_efficacy_signal="neutral",
            affect_valence="neutral",
            cognitive_load="low",
            interaction_risk="low",
            epistemic_balance="balanced",
            zpd_estimate="in",
            session_phase="exploration",
            session_maturity="low",
            evidence_strength="low",
            intervention_necessity="high",
            contradiction_status="none",
            concept_clarity="low",
            available_material="medium",
            conversation_goal="elicit_concrete_action",
            current_phase="exploration",
            emotional_state="neutral",
            action_feasibility="medium",
            autonomy_level="medium",
            recent_progress="unclear",
            need_recap=False,
            need_encouragement=False,
            need_reframing=False,
            can_close_for_now=False,
        )
        decision = ConversationDecision(
            primary_intent="elicit_concrete_action",
            pedagogical_move="elicit_action",
            number_of_questions=1,
            question_style="simple_open",
            should_explain_briefly=False,
            should_recap=False,
            should_encourage=False,
            should_reframe=False,
            should_close=False,
            response_constraints=["single_question_default"],
        )

        plan = build_teaching_plan(
            learner_slice=learner_slice,
            learning_stage=learning_stage,
            pedagogical_profile=pedagogical_profile,
            user_input={"content": "texte"},
            max_questions_per_turn=1,
            turn_state=turn_state,
            conversation_decision=decision,
        )

        self.assertEqual(plan.primary_intent, "elicit_concrete_action")
        self.assertEqual(plan.pedagogical_move, "elicit_action")
        self.assertEqual(plan.coverage_status, "action_missing")
        self.assertEqual(plan.ui_focus_label, "Faire émerger l'action réelle")
        self.assertEqual(plan.phase_source, "state_adapter")
