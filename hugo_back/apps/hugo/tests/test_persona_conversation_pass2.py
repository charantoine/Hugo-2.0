"""
Pass 2 — profils persona tuteur/formateur (baseline B).

Tags attendus : REL OBSERV PARTIEL pour comportements persona nouveaux.
"""
from __future__ import annotations

import pytest

from apps.accounts.models import Role
from apps.hugo.models import HugoSession, PersonaConversationProfile, TutorPrompt
from apps.hugo.services.hugo_orchestrator import build_hugo_turn
from apps.hugo.services.persona_session import is_persona_session, resolve_session_persona
from apps.hugo.services.tutor_workspace_bootstrap import (
    TUTOR_WORKSPACE_PROFILE_CODES,
    ensure_tutor_workspace_profiles,
)
from apps.hugo.services.trainer_persona_bootstrap import ensure_trainer_persona_profile
from apps.hugo.services.sqlite_schema_patches import ensure_persona_schema


@pytest.mark.django_db(transaction=True)
def test_ensure_sqlite_persona_schema_recreates_missing_persona_table():
    """Non-régression — baseline B sqlite sans migration 0022 appliquée."""
    from django.db import connection

    if connection.vendor != "sqlite":
        pytest.skip("sqlite only")

    ensure_persona_schema()
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS persona_conversation_profile")
    changes = ensure_persona_schema()
    assert "created persona_conversation_profile" in changes
    assert PersonaConversationProfile._meta.db_table in connection.introspection.table_names()
    assert ensure_persona_schema() == []


@pytest.mark.django_db
def test_tutor_workspace_bootstrap_creates_persona_profiles(organisation):
    """REL OBSERV PARTIEL — bootstrap P1 crée aussi PersonaConversationProfile miroir."""
    ensure_tutor_workspace_profiles(organisation)
    persona_rows = PersonaConversationProfile.objects.filter(
        organisation=organisation,
        persona=PersonaConversationProfile.Persona.TUTOR,
        status=PersonaConversationProfile.Status.ACTIVE,
    )
    assert persona_rows.count() == len(TUTOR_WORKSPACE_PROFILE_CODES)
    for code in TUTOR_WORKSPACE_PROFILE_CODES:
        row = persona_rows.get(code=code)
        assert row.tutor_prompt.persona_scope == TutorPrompt.PersonaScope.TUTOR


@pytest.mark.django_db
def test_trainer_persona_bootstrap_creates_default_profile(organisation):
    """REL OBSERV PARTIEL — seed formateur par défaut."""
    profile = ensure_trainer_persona_profile(organisation)
    assert profile.persona == PersonaConversationProfile.Persona.TRAINER
    assert profile.is_default is True
    assert profile.tutor_prompt.persona_scope == TutorPrompt.PersonaScope.TRAINER


@pytest.mark.django_db
def test_tutor_workspace_build_hugo_turn_renders_without_keyerror(morning_reconf_baseline_b):
    """CART CONFIRM fix — tutor_context_block injecté sans KeyError."""
    world = morning_reconf_baseline_b
    legacy = world.tutor_workspace_profiles["tutor_workspace_prep"]
    session = HugoSession.objects.create(
        organisation=world.organisation,
        learner=world.tutor,
        group=world.group,
        learner_conversation_profile=legacy,
        phase_classifier_enabled=False,
        p0_classifier_enabled=False,
    )
    assert resolve_session_persona(session) == PersonaConversationProfile.Persona.TUTOR
    turn = build_hugo_turn(session, {"content": "Je prépare un entretien avec mon apprenant."})
    assert "Mode conversation : tutor" in turn.system_prompt
    assert "Je prépare un entretien" in turn.user_prompt


@pytest.mark.django_db
def test_persona_conversation_profile_crud_and_preview(api_client, morning_reconf_baseline_b):
    """REL OBSERV PARTIEL — API CRUD + preview sans LLM."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.superadmin)

    create_resp = api_client.post(
        "/hugo/persona-conversation-profiles/",
        {
            "persona": "trainer",
            "code": "trainer_test_profile",
            "name": "Formateur test",
            "description": "Profil test Pass 2",
            "status": "active",
            "is_default": False,
            "system_template": "Contexte: {persona_context_block}\n{referential_block}",
            "user_template": "Question: {situation_content}",
        },
        format="json",
    )
    assert create_resp.status_code == 201, create_resp.data
    profile_id = create_resp.data["id"]

    list_resp = api_client.get("/hugo/persona-conversation-profiles/?persona=trainer")
    assert list_resp.status_code == 200
    codes = {row["code"] for row in list_resp.data}
    assert "trainer_test_profile" in codes

    preview_resp = api_client.post(
        f"/hugo/persona-conversation-profiles/{profile_id}/preview-render/",
        {"sample_content": "Exemple formateur"},
        format="json",
    )
    assert preview_resp.status_code == 200
    assert "Exemple formateur" in preview_resp.data["user_prompt"]
    assert "persona_context_block" in preview_resp.data["available_variables"]


@pytest.mark.django_db
def test_session_with_persona_profile_id(api_client, morning_reconf_baseline_b):
    """REL OBSERV PARTIEL — affectation persona_conversation_profile_id sur session."""
    world = morning_reconf_baseline_b
    persona = PersonaConversationProfile.objects.filter(
        organisation=world.organisation,
        persona=PersonaConversationProfile.Persona.TUTOR,
        code="tutor_workspace_prep",
    ).first()
    assert persona is not None

    api_client.force_authenticate(user=world.tutor)
    response = api_client.post(
        "/hugo/sessions/",
        {
            "group": str(world.group.id),
            "persona_conversation_profile_id": str(persona.id),
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["persona_conversation_profile"]["code"] == "tutor_workspace_prep"


@pytest.mark.django_db
def test_persona_session_skips_evaluation_and_synthesis(api_client, morning_reconf_baseline_b):
    """REL OBSERV PARTIEL — CTA éval/synthèse absents pour sessions persona (404)."""
    world = morning_reconf_baseline_b
    legacy = world.tutor_workspace_profiles["tutor_workspace_prep"]
    session = HugoSession.objects.create(
        organisation=world.organisation,
        learner=world.tutor,
        group=world.group,
        learner_conversation_profile=legacy,
    )
    assert is_persona_session(session)

    api_client.force_authenticate(user=world.tutor)
    eval_ready = api_client.get(f"/hugo/sessions/{session.id}/evaluation-readiness/")
    assert eval_ready.status_code == 404
    eval_req = api_client.post(f"/hugo/sessions/{session.id}/request-evaluation/", {}, format="json")
    assert eval_req.status_code == 404
    synth_req = api_client.post(f"/hugo/sessions/{session.id}/request-synthesis/", {}, format="json")
    assert synth_req.status_code == 404


@pytest.mark.django_db
def test_learner_session_not_persona(morning_reconf_baseline_b):
    """REL OBSERV — sessions apprenant inchangées (pas persona)."""
    world = morning_reconf_baseline_b
    session = HugoSession.objects.create(
        organisation=world.organisation,
        learner=world.learner,
        group=world.group,
    )
    assert resolve_session_persona(session) is None
    assert is_persona_session(session) is False


@pytest.mark.django_db
def test_trainer_role_session_detected_as_persona(morning_reconf_baseline_b):
    """REL OBSERV PARTIEL — rôle TRAINER sans profil apprenant → persona trainer."""
    world = morning_reconf_baseline_b
    ensure_trainer_persona_profile(world.organisation)
    session = HugoSession.objects.create(
        organisation=world.organisation,
        learner=world.trainer,
        group=world.group,
    )
    assert resolve_session_persona(session) == PersonaConversationProfile.Persona.TRAINER
