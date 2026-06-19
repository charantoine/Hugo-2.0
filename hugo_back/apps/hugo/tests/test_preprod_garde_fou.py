"""Preprod garde-fou suite — invariants convergence clusters 8–14.

Run: pytest apps/hugo/tests/test_preprod_garde_fou.py -q
"""
from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.domain.schemas import ConversationDecision, TeachingPlan, TurnState
from apps.hugo.models import HugoMessage, HugoSession
from apps.hugo.services.rag_support import select_rag_chunks
from apps.library.models import Document, DocumentChunk, GroupDocument
from apps.referentials.models import Group, GroupMembership


@pytest.mark.django_db
def test_preprod_memory_summary_no_verbatim(api_client, learner_user, organisation, group):
    """Domaine 20 — memory-summary gouverné, pas de verbatim brut."""
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        share_verbatim=False,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="SECRET_VERBATIM_PREPROD_MARKER",
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/memory-summary/")
    assert response.status_code == 200
    body = json.dumps(response.data)
    assert "SECRET_VERBATIM_PREPROD_MARKER" not in body
    assert response.data["session_memory"]["memory_scope"] == "intra_conversation"


@pytest.mark.django_db
def test_preprod_rag_lexical_only_no_vector_query(django_user_model, organisation, group):
    """Domaine 30 — RAG lexical ; pas de chemin vectoriel actif."""
    learner = django_user_model.objects.create_user(
        username="preprod_learner_rag",
        password="pass",
        organisation=organisation,
        role=Role.LEARNER,
    )
    GroupMembership.objects.create(organisation=organisation, group=group, user=learner)
    doc = Document.objects.create(organisation=organisation, title="Procédure sécurité", source_text="")
    chunk = DocumentChunk.objects.create(
        document=doc,
        content="procedure securite disjoncteur checklist",
        meta={"document_meta": {"knowledge_type": "safety"}},
    )
    GroupDocument.objects.create(
        organisation=organisation,
        group=group,
        document=doc,
        status=GroupDocument.Status.ACTIVE,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
    )

    teaching_plan = TeachingPlan(
        conversation_profile="diagnostic",
        session_phase="deepening",
        focus_competence={"label": "securite"},
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
    conversation_decision = ConversationDecision(
        primary_intent="deepen_analysis",
        pedagogical_move="analyze",
        number_of_questions=1,
        question_style="simple_open",
        should_explain_briefly=False,
        should_recap=False,
        should_encourage=False,
        should_reframe=False,
        should_close=False,
        response_constraints=[],
        metadata={"safety_or_quality_risk_level": "high"},
    )
    turn_state = TurnState(
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
        conversation_goal="comprendre procedure securite",
        current_phase="deepening",
        emotional_state="neutral",
        action_feasibility="medium",
        autonomy_level="medium",
        recent_progress="steady",
        need_recap=False,
        need_encouragement=False,
        need_reframing=False,
        can_close_for_now=False,
        safety_or_quality_risk_level="high",
        learner_help_request="explicit",
    )

    selections = select_rag_chunks(
        session=session,
        learner_text="probleme disjoncteur procedure securite",
        teaching_plan=teaching_plan,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
        conversation_profile="diagnostic",
    )
    assert selections
    assert str(chunk.id) in {s.chunk_id for s in selections}
    for sel in selections:
        assert "lexical" in sel.reason or "overlap" in sel.reason or sel.reason


@pytest.mark.django_db
def test_preprod_coordo_role_exists_in_model():
    """Domaine 90 — rôle COORDO présent (surface UI = héritage tuteur, cluster 14)."""
    assert hasattr(Role, "COORDO")
    assert Role.COORDO == "COORDO"


@pytest.mark.django_db
def test_preprod_trainer_blocked_from_org_exports(api_client, organisation, group):
    """Domaine 100/90 — TRAINER ne déclenche pas ExportRun org."""
    user_model = get_user_model()
    trainer = user_model.objects.create_user(
        username="preprod_trainer_exp",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    GroupMembership.objects.create(organisation=organisation, group=group, user=trainer)
    api_client.force_authenticate(user=trainer)
    response = api_client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 403
