from types import SimpleNamespace

import pytest
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoMessage, HugoSession
from apps.hugo.services.teaching_plan_builder import build_teaching_plan
from apps.library.models import Document, DocumentChunk, RagCitation
from apps.referentials.models import (
    Group,
    GroupMembership,
    Referential,
    ReferentialConfig,
    ReferentialCriterion,
    ReferentialItem,
    ReferentialItemOverlay,
)
from apps.hugo.domain.schemas import ConversationDecision, LearnerStateSlice, LearningStage, PedagogicalProfile, TurnState
from apps.hugo.services.context_builder import build_hugo_context


class OverlayCalibrationTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Org Overlay")
        user_model = __import__("django.contrib.auth").contrib.auth.get_user_model()
        self.learner = user_model.objects.create_user(
            username="learner_overlay",
            password="pass",
            organisation=self.org,
        )
        self.group = Group.objects.create(organisation=self.org, name="G Overlay")
        referential = Referential.objects.create(
            organisation=self.org,
            name="Ref Overlay",
            source_ref="RNCP-Overlay",
        )
        ReferentialConfig.objects.create(
            organisation=self.org,
            group=self.group,
            referential=referential,
        )
        item = ReferentialItem.objects.create(
            organisation=self.org,
            referential=referential,
            code="C2",
            title="Diagnostiquer une panne",
        )
        criterion = ReferentialCriterion.objects.create(
            organisation=self.org,
            referential_item=item,
            code="C2.1",
            label="Identifier l'origine de la panne",
            order_index=0,
        )
        ReferentialItemOverlay.objects.create(
            organisation=self.org,
            group=self.group,
            referential_item=item,
            coach_questions=["Quelle verification t'a permis d'isoler la cause ?"],
            common_mistakes=["Changer une piece sans confirmer le diagnostic"],
            example_situations=["Panne intermittente sur tableau secondaire"],
            example_evidence=[{"label": "Mesure avant remplacement"}],
            linked_documents=[{"document_id": "doc-1", "reason": "procedure de diagnostic"}],
        )
        self.session = HugoSession.objects.create(
            organisation=self.org,
            learner=self.learner,
            group=self.group,
        )

    def test_teaching_plan_reuses_overlay_signals(self):
        ctx = build_hugo_context(self.session)
        learner_slice = LearnerStateSlice(
            learner_id=str(self.learner.id),
            group_id=str(self.group.id),
            focus_candidates=[
                {
                    "item_id": ctx.items_to_focus[0].id,
                    "label": ctx.items_to_focus[0].title,
                    "criterion_id": ctx.items_to_focus[0].criteria[0].id,
                    "criterion_code": ctx.items_to_focus[0].criteria[0].code,
                    "criterion_label": ctx.items_to_focus[0].criteria[0].label,
                    "covered_criteria_codes": [],
                    "coach_questions": ctx.items_to_focus[0].coach_questions,
                    "common_mistakes": ctx.items_to_focus[0].common_mistakes,
                    "example_situations": ctx.items_to_focus[0].example_situations,
                    "example_evidence": ctx.items_to_focus[0].example_evidence,
                    "linked_documents": ctx.items_to_focus[0].linked_documents,
                }
            ],
            open_action_items=[],
            signals={},
        )
        learning_stage = LearningStage(
            group_id=str(self.group.id),
            item_id="",
            stage="intermediate",
            expected_level_now="participe",
            final_target_level="maitrise",
            priority="medium",
            intermediate_objective_label="",
        )
        profile = PedagogicalProfile(
            group_id=str(self.group.id),
            item_id="",
            focus_weights={"task": 0.3, "reasoning": 0.5, "metacognition": 0.2},
            directive_level="balanced",
            risk_sensitivity="normal",
        )
        state = TurnState(
            episode_clarity="high",
            has_concrete_actions=True,
            problem_salience="high",
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
            evidence_strength="medium",
            intervention_necessity="high",
            contradiction_status="none",
            concept_clarity="high",
            available_material="medium",
            conversation_goal="deepen_analysis",
            current_phase="deepening",
            emotional_state="neutral",
            action_feasibility="medium",
            autonomy_level="medium",
            recent_progress="steady",
            need_recap=False,
            need_encouragement=False,
            need_reframing=False,
            can_close_for_now=False,
        )
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

        plan = build_teaching_plan(
            learner_slice=learner_slice,
            learning_stage=learning_stage,
            pedagogical_profile=profile,
            user_input={"content": "J'ai diagnostique la panne."},
            max_questions_per_turn=1,
            turn_state=state,
            conversation_decision=decision,
        )

        self.assertIn("Quelle verification t'a permis d'isoler la cause ?", plan.coach_questions_candidates)
        self.assertIn("Changer une piece sans confirmer le diagnostic", plan.critical_mistakes)
        self.assertEqual(plan.focus_competence["example_evidence"][0], "Mesure avant remplacement")


class TurnReviewViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organisation.objects.create(name="Org Review")
        user_model = __import__("django.contrib.auth").contrib.auth.get_user_model()
        self.learner = user_model.objects.create_user(
            username="learner_review",
            password="pass",
            organisation=self.org,
            role=Role.LEARNER,
        )
        self.admin = user_model.objects.create_user(
            username="admin_review",
            password="pass",
            organisation=self.org,
            role=Role.ORGADMIN,
        )
        self.group = Group.objects.create(organisation=self.org, name="G Review")
        GroupMembership.objects.create(organisation=self.org, group=self.group, user=self.learner)
        self.session = HugoSession.objects.create(
            organisation=self.org,
            learner=self.learner,
            group=self.group,
        )
        self.learner_msg = HugoMessage.objects.create(
            organisation=self.org,
            session=self.session,
            role=HugoMessage.Role.LEARNER,
            content="J'ai suivi la procedure.",
            llm_request_payload={
                "conversation_profile": "diagnostic",
                "turn_state": {"episode_clarity": "high"},
                "conversation_progress": {"active_objective": "Isoler le point qui bloque", "percent": 40},
                "ui_state": {"tutor_signals": {"conversation_profile": "diagnostic"}},
                "session_memory": {"summary": "Capitaliser sur les repères déjà stabilisés."},
            },
        )
        self.assistant_msg = HugoMessage.objects.create(
            organisation=self.org,
            session=self.session,
            role=HugoMessage.Role.ASSISTANT,
            content="Qu'as-tu verifie ensuite ?",
            llm_response_payload={"raw_response": {"ok": True}},
        )
        document = Document.objects.create(organisation=self.org, title="Procedure review")
        chunk = DocumentChunk.objects.create(document=document, content="Checklist review", meta={})
        RagCitation.objects.create(
            organisation=self.org,
            message=self.assistant_msg,
            document=document,
            chunk=chunk,
            score=2.0,
            meta={"reason": "test"},
        )

    @override_settings(HUGO_DEBUG_TRACING=True)
    def test_learner_can_review_own_turn(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(f"/internal/hugo/sessions/{self.session.id}/turn-review/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["session"]["id"], str(self.session.id))
        self.assertEqual(response.data["learner_message"]["id"], str(self.learner_msg.id))
        self.assertTrue(response.data["rag_citations"])

    @override_settings(HUGO_DEBUG_TRACING=True)
    def test_admin_can_review_turn(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/internal/hugo/sessions/{self.session.id}/turn-review/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pilotage"]["conversation_profile"], "diagnostic")

    @override_settings(HUGO_DEBUG_TRACING=False)
    def test_turn_review_returns_404_when_tracing_disabled(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(f"/internal/hugo/sessions/{self.session.id}/turn-review/")
        self.assertEqual(response.status_code, 404)

    def test_admin_can_read_session_pilotage_snapshot(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/internal/hugo/sessions/{self.session.id}/pilotage/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["conversation_profile"], "diagnostic")
        self.assertEqual(response.data["conversation_progress"]["percent"], 40)
