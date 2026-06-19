from types import SimpleNamespace

import pytest
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from apps.hugo.domain.schemas import TeachingPlan, TurnState, ConversationDecision
from apps.hugo.models import HugoSession, HugoMessage, TutorPrompt
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt
from apps.hugo.services.rag_support import RagSelection, select_rag_chunks
from apps.hugo.services.tracing import (
    build_prompt_sources,
    build_request_trace,
    build_response_trace,
)
from apps.hugo.services.context_builder import HugoContext
from apps.library.models import Document, DocumentChunk, GroupDocument, RagCitation


class RagSupportUnitTests(SimpleTestCase):
    def _state(self, **overrides):
        state = TurnState(
            episode_clarity="high",
            has_concrete_actions=True,
            problem_salience="high",
            reflection_phase="analysis",
            reflective_depth="high",
            self_efficacy_signal="neutral",
            affect_valence="neutral",
            cognitive_load="medium",
            interaction_risk="high",
            epistemic_balance="balanced",
            zpd_estimate="in",
            session_phase="deepening",
            session_maturity="medium",
            evidence_strength="medium",
            intervention_necessity="high",
            contradiction_status="none",
            concept_clarity="high",
            available_material="high",
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
            metadata={"safety_or_quality_risk_level": "high"},
        )
        for key, value in overrides.items():
            setattr(decision, key, value)
        return decision

    @override_settings(HUGO_DEBUG_TRACING=False)
    def test_build_request_trace_always_includes_llm_inputs_when_disabled(self):
        payload = build_request_trace(
            provider="ollama",
            llm_meta={"provider": "ollama", "model_used": "mistral"},
            system_prompt="system",
            user_prompt="user",
            max_tokens=150,
            resolved_tutor_prompt_id=None,
            configured_output_mode="reflection_block",
            output_mode="single_question",
            effective_max_questions_this_turn=1,
            session_phase="exploration",
            next_session_phase="deepening",
            requested_phase=None,
            manual_phase_override=None,
            alignment_meta={},
            phase_decision={},
            p0_classifier={},
            turn_state={},
            conversation_decision={},
            conversation_profile="reflective_afest",
            conversation_progress={},
            ui_state={},
            session_memory={},
            focus_criterion_code="",
            focus_criterion_label="",
            covered_criteria_codes=[],
            rag_selections=[],
        )
        self.assertEqual(payload["provider"], "ollama")
        self.assertEqual(payload["system_prompt"], "system")
        self.assertEqual(payload["user_prompt"], "user")
        self.assertNotIn("phase_classifier_provider", payload)
        self.assertIn("prompt_sources", payload)
        self.assertFalse(payload["prompt_sources"]["referential"]["included"])
        self.assertEqual(payload["rag"], [])
        self.assertIsNone(payload["resolved_tutor_prompt_id"])
        self.assertEqual(payload["tutor_prompt_snapshot"], {})
        self.assertEqual(payload["conversation_profile"], "reflective_afest")
        self.assertEqual(payload["conversation_progress"], {})
        self.assertEqual(payload["ui_state"], {})
        self.assertEqual(payload["session_memory"], {})

    @override_settings(HUGO_DEBUG_TRACING=False)
    def test_minimal_request_trace_lists_rag_when_selections_present(self):
        sel = RagSelection(
            chunk_id="chunk-1",
            document_id="doc-1",
            document_title="Procédure",
            content="extrait",
            score=0.88,
            reason="support",
            meta={},
        )
        payload = build_request_trace(
            provider="ollama",
            llm_meta={"provider": "ollama", "model_used": "mistral"},
            system_prompt="system",
            user_prompt="user",
            max_tokens=150,
            resolved_tutor_prompt_id=None,
            configured_output_mode="reflection_block",
            output_mode="single_question",
            effective_max_questions_this_turn=1,
            session_phase="exploration",
            next_session_phase="deepening",
            requested_phase=None,
            manual_phase_override=None,
            alignment_meta={},
            phase_decision={},
            p0_classifier={},
            turn_state={},
            conversation_decision={},
            conversation_profile="reflective_afest",
            conversation_progress={},
            ui_state={},
            session_memory={},
            focus_criterion_code="",
            focus_criterion_label="",
            covered_criteria_codes=[],
            rag_selections=[sel],
        )
        self.assertEqual(len(payload["rag"]), 1)
        self.assertEqual(payload["rag"][0]["chunk_id"], "chunk-1")
        self.assertEqual(payload["rag"][0]["document_title"], "Procédure")
        self.assertTrue(payload["prompt_sources"]["rag"]["used"])
        self.assertEqual(payload["prompt_sources"]["rag"]["selection_count"], 1)
        self.assertIn("anti_loop", payload)
        self.assertEqual(payload["tutor_prompt_snapshot"], {})
        self.assertEqual(payload["anti_loop"]["consecutive_clarify_turns"], 0)
        self.assertEqual(payload["conversation_profile"], "reflective_afest")

    @override_settings(HUGO_DEBUG_TRACING=False)
    def test_minimal_response_trace_lists_rag_when_selections_present(self):
        sel = RagSelection(
            chunk_id="c1",
            document_id="d1",
            document_title="Doc",
            content="x",
            score=0.5,
            reason="r",
            meta={},
        )
        payload = build_response_trace(
            provider="ollama",
            llm_meta={"provider": "ollama"},
            rag_selections=[sel],
            assistant_text_before_guardrails="avant",
        )
        self.assertEqual(len(payload["rag"]), 1)
        self.assertEqual(payload["rag"][0]["document_id"], "d1")
        self.assertTrue(payload["prompt_sources"]["rag"]["used"])

    def test_build_prompt_sources_referential_when_context_has_name(self):
        ctx = HugoContext(
            referential_name="Réf. test",
            referential_source_ref=None,
            items_to_focus=[],
            items_already_covered=[],
            learner_summary=None,
            recent_traces_info=[],
            class_documents=[],
        )
        ps = build_prompt_sources(ctx, [])
        self.assertTrue(ps["referential"]["included"])
        self.assertEqual(ps["referential"]["referential_name"], "Réf. test")
        self.assertEqual(ps["referential"]["focus_items_count"], 0)
        self.assertFalse(ps["rag"]["used"])

    def test_renderer_appends_rag_block_to_documents(self):
        tutor_prompt = SimpleNamespace(
            system_template="{documents_block}",
            user_template="{situation_content}",
        )
        session = SimpleNamespace(organisation_id="org", id="sess")
        ctx = HugoContext(
            referential_name=None,
            referential_source_ref=None,
            items_to_focus=[],
            items_already_covered=[],
            learner_summary=None,
            recent_traces_info=[],
            class_documents=["Procedure tableau"],
        )
        teaching_plan = TeachingPlan(
            conversation_profile="reflective_afest",
            session_phase="deepening",
            focus_competence={},
            learning_stage="intermediate",
            expected_level_now="participe",
            current_level="structured",
            coverage_status="ok",
            regulation_targets={"reasoning": 0.7},
            open_action_items=[],
            critical_mistakes=[],
            coach_questions_candidates=[],
            rag_mode="supporting",
            ui_focus_label="Approfondir",
            max_questions_this_turn=1,
        )
        rendered = render_with_tutor_prompt(
            tutor_prompt=tutor_prompt,
            session=session,
            ctx=ctx,
            content="texte",
            teaching_plan=teaching_plan,
            rag_chunks=["Procedure tableau | score=2.00 | extrait=Verifier la consignation avant intervention"],
        )
        self.assertIn("Appuis documentaires situés", rendered.system_prompt)
        self.assertIn("Procedure tableau", rendered.system_prompt)


@pytest.mark.django_db
def test_select_rag_chunks_prioritizes_procedure_documents(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_rag", organisation=organisation)
    session = HugoSession.objects.create(organisation=organisation, learner=learner, group=group)
    procedure_doc = Document.objects.create(
        organisation=organisation,
        title="Procedure securite tableau",
        meta={"knowledge_type": "diagnostic", "trainer_priority": "high", "intended_profiles": ["reflective_afest", "diagnostic"]},
    )
    other_doc = Document.objects.create(organisation=organisation, title="Cours general electricite")
    GroupDocument.objects.create(organisation=organisation, group=group, document=procedure_doc)
    GroupDocument.objects.create(organisation=organisation, group=group, document=other_doc)
    procedure_chunk = DocumentChunk.objects.create(
        document=procedure_doc,
        content="Procedure de securite et checklist avant intervention sur tableau electrique",
        meta={"tags": ["procedure", "securite"]},
    )
    DocumentChunk.objects.create(
        document=other_doc,
        content="Rappel theorique general sur le courant electrique",
        meta={"tags": ["cours"]},
    )
    teaching_plan = TeachingPlan(
        conversation_profile="reflective_afest",
        session_phase="deepening",
        focus_competence={"label": "Intervenir en securite", "criterion_label": "Respecter la procedure"},
        learning_stage="intermediate",
        expected_level_now="participe",
        current_level="structured",
        coverage_status="ok",
        regulation_targets={"reasoning": 0.7},
        open_action_items=[],
        critical_mistakes=[],
        coach_questions_candidates=[],
        rag_mode="supporting",
        ui_focus_label="Approfondir",
        max_questions_this_turn=1,
    )
    state = TurnState(
        episode_clarity="high",
        has_concrete_actions=True,
        problem_salience="high",
        reflection_phase="analysis",
        reflective_depth="high",
        self_efficacy_signal="neutral",
        affect_valence="neutral",
        cognitive_load="medium",
        interaction_risk="high",
        epistemic_balance="balanced",
        zpd_estimate="in",
        session_phase="deepening",
        session_maturity="medium",
        evidence_strength="medium",
        intervention_necessity="high",
        contradiction_status="none",
        concept_clarity="high",
        available_material="high",
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

    selections = select_rag_chunks(
        session=session,
        learner_text="J'ai suivi la procedure de securite sur le tableau mais je veux verifier la checklist.",
        teaching_plan=teaching_plan,
        turn_state=state,
        conversation_decision=decision,
    )

    assert selections
    assert selections[0].chunk_id == str(procedure_chunk.id)
    assert "Procedure securite tableau" in selections[0].document_title


@pytest.mark.django_db
def test_select_rag_chunks_prioritizes_trainer_profile_documents(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_profiled_rag", organisation=organisation)
    session = HugoSession.objects.create(organisation=organisation, learner=learner, group=group)
    revision_doc = Document.objects.create(
        organisation=organisation,
        title="Checklist révision moteur",
        meta={"knowledge_type": "revision", "trainer_priority": "high", "intended_profiles": ["knowledge_review"]},
    )
    reflective_doc = Document.objects.create(
        organisation=organisation,
        title="Questions réflexives atelier",
        meta={"knowledge_type": "reflection", "intended_profiles": ["reflective_afest"]},
    )
    GroupDocument.objects.create(organisation=organisation, group=group, document=revision_doc)
    GroupDocument.objects.create(organisation=organisation, group=group, document=reflective_doc)
    revision_chunk = DocumentChunk.objects.create(
        document=revision_doc,
        content="Checklist de révision moteur et méthode de contrôle avant remise sous tension",
        meta={"document_meta": revision_doc.meta},
    )
    DocumentChunk.objects.create(
        document=reflective_doc,
        content="Question réflexive sur le vécu en atelier et le ressenti apprenant",
        meta={"document_meta": reflective_doc.meta},
    )
    teaching_plan = TeachingPlan(
        conversation_profile="knowledge_review",
        session_phase="deepening",
        focus_competence={"label": "Réviser une procédure", "criterion_label": "Retenir la checklist"},
        learning_stage="intermediate",
        expected_level_now="participe",
        current_level="structured",
        coverage_status="ok",
        regulation_targets={"reasoning": 0.6},
        open_action_items=[],
        critical_mistakes=[],
        coach_questions_candidates=[],
        rag_mode="supporting",
        ui_focus_label="Stabiliser le repère utile",
        max_questions_this_turn=1,
    )
    state = TurnState(
        episode_clarity="high",
        has_concrete_actions=True,
        problem_salience="medium",
        reflection_phase="analysis",
        reflective_depth="medium",
        self_efficacy_signal="neutral",
        affect_valence="neutral",
        cognitive_load="low",
        interaction_risk="low",
        epistemic_balance="balanced",
        zpd_estimate="in",
        session_phase="deepening",
        session_maturity="medium",
        evidence_strength="medium",
        intervention_necessity="medium",
        contradiction_status="none",
        concept_clarity="high",
        available_material="high",
        conversation_goal="stabilize_knowledge",
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
        primary_intent="stabilize_knowledge",
        pedagogical_move="assist",
        number_of_questions=1,
        question_style="simple_open",
        should_explain_briefly=True,
        should_recap=False,
        should_encourage=False,
        should_reframe=False,
        should_close=False,
        response_constraints=["anchor_to_known_rule"],
    )

    selections = select_rag_chunks(
        session=session,
        learner_text="Je veux réviser la checklist moteur avant la remise sous tension.",
        teaching_plan=teaching_plan,
        turn_state=state,
        conversation_decision=decision,
        conversation_profile="knowledge_review",
    )

    assert selections
    assert selections[0].chunk_id == str(revision_chunk.id)


@pytest.mark.django_db
def test_select_rag_chunks_skips_low_risk_turns(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_rag_lowrisk", organisation=organisation)
    session = HugoSession.objects.create(organisation=organisation, learner=learner, group=group)
    document = Document.objects.create(organisation=organisation, title="Procedure securite tableau")
    GroupDocument.objects.create(organisation=organisation, group=group, document=document)
    DocumentChunk.objects.create(
        document=document,
        content="Procedure de securite et checklist avant intervention sur tableau electrique",
        meta={"tags": ["procedure", "securite"]},
    )
    teaching_plan = TeachingPlan(
        conversation_profile="reflective_afest",
        session_phase="deepening",
        focus_competence={"label": "Intervenir en securite", "criterion_label": "Respecter la procedure"},
        learning_stage="intermediate",
        expected_level_now="participe",
        current_level="structured",
        coverage_status="ok",
        regulation_targets={"reasoning": 0.7},
        open_action_items=[],
        critical_mistakes=[],
        coach_questions_candidates=[],
        rag_mode="supporting",
        ui_focus_label="Approfondir",
        max_questions_this_turn=1,
    )
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
        evidence_strength="medium",
        intervention_necessity="high",
        contradiction_status="none",
        concept_clarity="high",
        available_material="high",
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
        safety_or_quality_risk_level="low",
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
        metadata={"safety_or_quality_risk_level": "low"},
    )

    selections = select_rag_chunks(
        session=session,
        learner_text="J'ai suivi la procedure sur le tableau.",
        teaching_plan=teaching_plan,
        turn_state=state,
        conversation_decision=decision,
    )

    assert selections == []


@pytest.mark.django_db
@override_settings(HUGO_DEBUG_TRACING=True)
@patch("apps.hugo.views_sessions.complete_with_provider")
def test_message_pipeline_persists_rag_citations(
    complete_mock, api_client, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_rag_pipeline",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_rag",
        name="AFEST RAG",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{documents_block}",
        user_template="{situation_content}",
        max_questions_per_turn=2,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )
    document = Document.objects.create(organisation=organisation, title="Procedure tableau")
    GroupDocument.objects.create(organisation=organisation, group=group, document=document)
    DocumentChunk.objects.create(
        document=document,
        content="Checklist procedure tableau electrique avant intervention et verification des risques",
        meta={"tags": ["procedure", "checklist"]},
    )
    complete_mock.return_value = (
        "Qu'as-tu verifie en premier sur le tableau ?",
        {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock": True}, "raw_response": {"ok": True}},
    )

    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(
        url,
        {"content": "J'ai suivi la procedure sur le tableau et je veux confirmer la checklist de securite."},
        format="json",
    )

    assert response.status_code == 200
    learner_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).latest("created_at")
    assistant_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.ASSISTANT).latest("created_at")
    assert learner_msg.llm_request_payload["rag"]
    assert learner_msg.llm_request_payload["ui_state"]["supporting_documents"]
    assert assistant_msg.llm_response_payload["rag"]
    assert RagCitation.objects.filter(message=assistant_msg).exists()
    assert response.data["rag_citations"]
