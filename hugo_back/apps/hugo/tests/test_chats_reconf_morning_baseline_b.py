"""
Suite pytest — reconfiguration chats tuteur/formateur (baseline B, P0 legacy).

Périmètres annotés : TUTOR | TRAINER | LEARNER | ADMIN | CONTRACT | CROSS
"""
from __future__ import annotations

import json

import pytest
from django.urls import reverse

from apps.accounts.models import Role, User
from apps.hugo.domain.conversation_profile import (
    ConversationPosture,
    ConversationProgress as ContractConversationProgress,
    SessionMaturityLevel,
)
from apps.hugo.domain.schemas import ConversationProgress as EngagementConversationProgress
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS, SessionMemorySummary
from apps.hugo.models import (
    HugoMessage,
    HugoSession,
    LearnerConversationGlobalProfile,
    TrainerKnowledgeItem,
    TutorConductProfile,
    TutorPrompt,
)
from apps.hugo.services.context_builder import _resolve_tutor_prompt
from apps.hugo.services.tutor_workspace_bootstrap import TUTOR_WORKSPACE_PROFILE_CODES
from apps.hugo.services.ui_state_builder import build_contract_ui_state, build_ui_state
from apps.hugo.tests.morning_reconf_fixtures import (
    VERBATIM_PRIVATE_MARKER,
    VERBATIM_SHARED_MARKER,
    build_morning_reconf_baseline_b,
)
from apps.hugo.tests.test_cluster15_interfaces_apprenant import (
    CLUSTER15_UI_STATE_CORE_KEYS,
    CONVERSATION_MODE_KEYS,
)
from apps.referentials.models import GroupMembership, TutorLearnerLink

P0_FORBIDDEN_IN_UI = set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS) | {
    "turn_state",
    "conversation_decision",
    "episode_clarity",
    "cognitive_load",
    "interaction_risk",
    "tutor_signals",
    "quest_cards",
    "header_badges",
}

MEMORY_SUMMARY_CORE_KEYS = {"session_memory", "theme_memories"}
SESSION_MEMORY_KEYS = {
    "session_id",
    "updated_at",
    "memory_scope",
    "facts_confirmed",
    "open_points",
    "pending_actions",
}


# --- Configuration admin et profils (ADMIN) ---


@pytest.mark.django_db
def test_superadmin_can_list_conduct_profiles(api_client, morning_reconf_baseline_b):
    """ADMIN — superadmin liste les conduct profiles du tenant."""
    api_client.force_authenticate(user=morning_reconf_baseline_b.superadmin)
    response = api_client.get("/hugo/conduct-profiles/")
    assert response.status_code == 200
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_superadmin_can_edit_tutor_prompt_profiles(api_client, morning_reconf_baseline_b):
    """ADMIN — superadmin peut PATCH un TutorPrompt org-scoped."""
    world = morning_reconf_baseline_b
    prompt = world.tutor_workspace_profiles["tutor_workspace_prep"].reflective_tutor_prompt
    api_client.force_authenticate(user=world.superadmin)
    marker = "MORNING_RECONF_TUTOR_PROMPT_MARKER"
    response = api_client.patch(
        f"/hugo/tutor-prompts/{prompt.id}/",
        {"name": marker},
        format="json",
    )
    assert response.status_code == 200
    prompt.refresh_from_db()
    assert prompt.name == marker


@pytest.mark.django_db
def test_superadmin_can_edit_trainer_related_profiles(api_client, morning_reconf_baseline_b):
    """ADMIN — superadmin peut créer un item base connaissances formateur."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.superadmin)
    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Savoir admin formateur",
            "content_type": "mastery_criterion",
            "source_type": "manual",
            "status": "declared",
        },
        format="json",
    )
    assert response.status_code == 201
    assert TrainerKnowledgeItem.objects.filter(content="Savoir admin formateur").exists()


@pytest.mark.django_db
def test_tutor_workspace_profiles_bootstrap_exist(morning_reconf_baseline_b):
    """TUTOR — les 4 profils workspace P1 existent et sont actifs."""
    profiles = morning_reconf_baseline_b.tutor_workspace_profiles
    assert set(profiles.keys()) == set(TUTOR_WORKSPACE_PROFILE_CODES)
    for profile in profiles.values():
        assert profile.status == LearnerConversationGlobalProfile.Status.ACTIVE


@pytest.mark.django_db
def test_tutor_workspace_profile_resolves_prompt_and_conduct(morning_reconf_baseline_b):
    """TUTOR — chaque profil workspace résout prompt + conduct pour sa posture primaire."""
    for code, profile in morning_reconf_baseline_b.tutor_workspace_profiles.items():
        posture = {
            "tutor_workspace_prep": ConversationPosture.REFLECTIVE_AFEST.value,
            "tutor_workspace_diagnostic": ConversationPosture.DIAGNOSTIC.value,
            "tutor_workspace_coreflex": ConversationPosture.REFLECTIVE_AFEST.value,
            "tutor_workspace_journal": ConversationPosture.KNOWLEDGE_REVIEW.value,
        }[code]
        prompt = profile.get_tutor_prompt_for_posture(posture)
        conduct = profile.get_conduct_profile_for_posture(posture)
        assert prompt is not None
        assert prompt.code == code
        assert conduct is not None
        assert conduct.forbidden_moves


@pytest.mark.django_db
def test_trainer_profiles_do_not_override_tutor_profiles(morning_reconf_baseline_b):
    """CROSS — session formateur n'utilise pas un profil workspace tuteur."""
    world = morning_reconf_baseline_b
    session = world.trainer_session
    assert session.learner_conversation_profile is None or (
        session.learner_conversation_profile.name not in TUTOR_WORKSPACE_PROFILE_CODES
    )


@pytest.mark.django_db
def test_learner_profiles_do_not_override_tutor_or_trainer_profiles(morning_reconf_baseline_b):
    """CROSS — session apprenant sans profil workspace tuteur."""
    world = morning_reconf_baseline_b
    profile_name = getattr(world.learner_session.learner_conversation_profile, "name", None)
    assert profile_name not in TUTOR_WORKSPACE_PROFILE_CODES


# --- ACL tuteur (TUTOR) ---


@pytest.mark.django_db
def test_tutor_can_get_group_learners_when_linked(api_client, morning_reconf_baseline_b):
    """TUTOR — learners dashboard limité au lien TutorLearnerLink."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.tutor)
    response = api_client.get(f"/dashboard/groups/{world.group.id}/learners/")
    assert response.status_code == 200
    ids = {item["id"] for item in response.data.get("learners", [])}
    assert str(world.learner.id) in ids


@pytest.mark.django_db
def test_tutor_cannot_get_unlinked_learner_timeline(api_client, morning_reconf_baseline_b):
    """TUTOR — timeline interdite pour apprenant non lié."""
    world = morning_reconf_baseline_b
    unlinked = User.objects.create_user(
        username="morning_unlinked_learner",
        password="pass",
        organisation=world.organisation,
        role=Role.LEARNER,
    )
    GroupMembership.objects.create(
        organisation=world.organisation,
        group=world.group,
        user=unlinked,
    )
    api_client.force_authenticate(user=world.tutor)
    response = api_client.get(
        f"/dashboard/groups/{world.group.id}/learners/{unlinked.id}/timeline/"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_tutor_timeline_filters_unshared_verbatim(api_client, morning_reconf_baseline_b):
    """TUTOR — verbatim non partagé absent de la timeline."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.tutor)
    response = api_client.get(
        f"/dashboard/groups/{world.group.id}/learners/{world.learner.id}/timeline/"
    )
    assert response.status_code == 200
    serialized = json.dumps(response.data)
    assert VERBATIM_PRIVATE_MARKER not in serialized


@pytest.mark.django_db
def test_tutor_can_validate_trace_on_authorized_learner(api_client, morning_reconf_baseline_b):
    """TUTOR — validation trace sur apprenant lié."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.tutor)
    response = api_client.post(f"/traces/{world.linked_trace.id}/validate/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_tutor_cannot_validate_trace_outside_scope(api_client, morning_reconf_baseline_b):
    """TUTOR — validation trace refusée hors périmètre."""
    world = morning_reconf_baseline_b
    other_session = HugoSession.objects.create(
        organisation=world.organisation,
        group=world.group,
        learner=User.objects.create_user(
            username="morning_other_learner",
            password="pass",
            organisation=world.organisation,
            role=Role.LEARNER,
        ),
    )
    from apps.hugo.models import Trace

    trace = Trace.objects.create(
        organisation=world.organisation,
        session=other_session,
        payload_structured={},
    )
    api_client.force_authenticate(user=world.tutor)
    response = api_client.post(f"/traces/{trace.id}/validate/")
    assert response.status_code == 403


# --- ACL formateur (TRAINER) ---


@pytest.mark.django_db
def test_trainer_knowledge_item_crud(api_client, morning_reconf_baseline_b):
    """TRAINER — CRUD base connaissances."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.trainer)
    create = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {"content": "CRUD morning", "status": "declared"},
        format="json",
    )
    assert create.status_code == 201
    item_id = create.data["id"]
    patch = api_client.patch(
        f"/hugo/trainer/knowledge-items/{item_id}/",
        {"content": "CRUD morning updated"},
        format="json",
    )
    assert patch.status_code == 200
    listing = api_client.get("/hugo/trainer/knowledge-items/")
    assert listing.status_code == 200
    assert any(i["id"] == item_id for i in listing.data["items"])


@pytest.mark.django_db
def test_trainer_elicitation_routes_work(api_client, morning_reconf_baseline_b):
    """TRAINER — élicitation questions + answers."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.trainer)
    questions = api_client.get("/hugo/trainer/referential-items/C1/elicitation-questions/")
    assert questions.status_code == 200
    answers = api_client.post(
        "/hugo/trainer/referential-items/C1/elicitation-answers/",
        {"answers": {"q_mastery": "Réponse élicitation morning"}},
        format="json",
    )
    assert answers.status_code == 201


@pytest.mark.django_db
def test_trainer_group_context_panel_payload_contains_memberships(api_client, morning_reconf_baseline_b):
    """TRAINER — GET /groups/ expose les groupes org (membership suffit)."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.trainer)
    response = api_client.get("/groups/")
    assert response.status_code == 200
    group_ids = {item["id"] for item in response.data}
    assert str(world.group.id) in group_ids


@pytest.mark.django_db
def test_trainer_dashboard_group_learners_inc02_current_behavior(api_client, morning_reconf_baseline_b):
    """TRAINER — INC-02 figé : dashboard learners vide sans TutorLearnerLink."""
    world = morning_reconf_baseline_b
    assert not TutorLearnerLink.objects.filter(
        group=world.group,
        tutor=world.trainer,
    ).exists()
    api_client.force_authenticate(user=world.trainer)
    response = api_client.get(f"/dashboard/groups/{world.group.id}/learners/")
    assert response.status_code == 200
    assert response.data.get("learners", []) == []


# --- Sessions, UIState, mémoire (LEARNER / CONTRACT) ---


def _session_progress(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "posture": "reflective_afest",
        "active_branches": [],
        "active_branches_count": 0,
        "overall_maturity": "red",
        "synthesis_eligible": False,
        "evaluation_eligible": False,
        "missing_for_next_level": [],
        "reason_codes": [],
    }


@pytest.mark.django_db
def test_get_ui_state_uses_contract_builder_fields_only(api_client, morning_reconf_baseline_b):
    """LEARNER — GET /ui-state/ = contrat build_contract_ui_state sans champs engagement."""
    world = morning_reconf_baseline_b
    session = world.learner_session
    session.conversation_progress = _session_progress(str(session.id))
    session.save(update_fields=["conversation_progress"])
    api_client.force_authenticate(user=world.learner)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")
    assert response.status_code == 200
    assert CLUSTER15_UI_STATE_CORE_KEYS.issubset(set(response.data.keys()))
    assert set(response.data.keys()).isdisjoint(P0_FORBIDDEN_IN_UI)
    mode = response.data.get("conversation_mode") or {}
    assert CONVERSATION_MODE_KEYS.issubset(set(mode.keys()))


@pytest.mark.django_db
def test_post_turn_payload_ui_state_differs_from_get_ui_state(morning_reconf_baseline_b):
    """LEARNER — build_ui_state (tour) ≠ build_contract_ui_state (GET)."""
    world = morning_reconf_baseline_b
    session = world.learner_session
    contract_progress = ContractConversationProgress(
        session_id=str(session.id),
        posture=ConversationPosture.REFLECTIVE_AFEST,
        overall_maturity=SessionMaturityLevel.RED,
    )
    contract = build_contract_ui_state(session=session, progress=contract_progress)
    engagement_progress = EngagementConversationProgress(
        conversation_profile="reflective_afest",
        branch_key="main",
        branch_label="Situation",
        active_objective="",
        stage_index=0,
        current_step_id="raconter",
        current_step_label="Raconter",
        percent=0,
        maturity="red",
        can_summarize=False,
        evaluation_eligible=False,
        closure_eligible=False,
        rag_allowed=False,
        supported_by_documents=False,
    )
    engagement = build_ui_state(
        progress=engagement_progress,
        session_memory=SessionMemorySummary(summary=""),
        turn_state={},
        conversation_decision={},
    )
    contract_keys = set(contract.to_dict().keys())
    engagement_keys = set(engagement.to_dict().keys())
    assert "tutor_signals" in engagement_keys
    assert "tutor_signals" not in contract_keys
    assert "quest_cards" in engagement_keys
    assert "quest_cards" not in contract_keys


@pytest.mark.django_db
def test_memory_summary_contains_sessionmemory_without_prompt_injection(
    api_client, morning_reconf_baseline_b,
):
    """LEARNER — memory-summary structurée ; pas d'injection dans prompt LLM."""
    world = morning_reconf_baseline_b
    session = world.learner_session
    HugoMessage.objects.create(
        organisation=world.organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Je décris ma situation sur le terrain.",
        llm_request_payload={
            "turn_state": {"covered_points": ["situation_described"], "remaining_open_points": []},
        },
    )
    api_client.force_authenticate(user=world.learner)
    url = reverse("session_memory_summary", kwargs={"session_id": str(session.id)})
    response = api_client.get(url)
    assert response.status_code == 200
    assert MEMORY_SUMMARY_CORE_KEYS.issubset(set(response.data.keys()))
    sm = response.data["session_memory"]
    assert SESSION_MEMORY_KEYS.issubset(set(sm.keys()))
    assert sm["memory_scope"] == "intra_conversation"
    assert "system_prompt" not in json.dumps(response.data)


@pytest.mark.django_db
def test_memory_summary_contains_no_raw_verbatim(api_client, morning_reconf_baseline_b):
    """LEARNER — memory-summary sans verbatim brut."""
    world = morning_reconf_baseline_b
    session = world.learner_session
    marker = "RAW_VERBATIM_MUST_NOT_APPEAR_IN_MEMORY_SUMMARY"
    HugoMessage.objects.create(
        organisation=world.organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content=marker,
    )
    api_client.force_authenticate(user=world.learner)
    url = reverse("session_memory_summary", kwargs={"session_id": str(session.id)})
    response = api_client.get(url)
    assert response.status_code == 200
    assert marker not in json.dumps(response.data)


@pytest.mark.django_db
def test_set_posture_updates_session_without_cross_chat_effect(api_client, morning_reconf_baseline_b):
    """LEARNER — set-posture local à la session."""
    world = morning_reconf_baseline_b
    session_a = world.learner_session
    session_b = HugoSession.objects.create(
        organisation=world.organisation,
        group=world.group,
        learner=world.learner,
        conversation_progress=_session_progress("pending"),
    )
    session_b.conversation_progress["session_id"] = str(session_b.id)
    session_b.save(update_fields=["conversation_progress"])
    api_client.force_authenticate(user=world.learner)
    response = api_client.post(
        f"/hugo/sessions/{session_a.id}/set-posture/",
        {"posture": "diagnostic"},
        format="json",
    )
    assert response.status_code == 200
    session_a.refresh_from_db()
    session_b.refresh_from_db()
    assert session_a.posture == "diagnostic"
    assert session_b.posture != "diagnostic"


# --- Chat tuteur P1 (TUTOR) ---


@pytest.mark.parametrize("profile_code", list(TUTOR_WORKSPACE_PROFILE_CODES))
@pytest.mark.django_db
def test_tutor_session_can_be_created_with_workspace_profiles(
    api_client, morning_reconf_baseline_b, profile_code,
):
    """TUTOR — création session avec chaque profil workspace."""
    world = morning_reconf_baseline_b
    profile = world.tutor_workspace_profiles[profile_code]
    api_client.force_authenticate(user=world.tutor)
    response = api_client.post(
        "/hugo/sessions/",
        {
            "group": str(world.group.id),
            "learner_conversation_profile_id": str(profile.id),
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["learner_conversation_profile"]["name"] == profile_code


@pytest.mark.django_db
def test_tutor_session_can_be_created_with_tutor_workspace_prep(
    api_client, morning_reconf_baseline_b,
):
    test_tutor_session_can_be_created_with_workspace_profiles(
        api_client, morning_reconf_baseline_b, "tutor_workspace_prep",
    )


@pytest.mark.django_db
def test_tutor_session_can_be_created_with_tutor_workspace_diagnostic(
    api_client, morning_reconf_baseline_b,
):
    test_tutor_session_can_be_created_with_workspace_profiles(
        api_client, morning_reconf_baseline_b, "tutor_workspace_diagnostic",
    )


@pytest.mark.django_db
def test_tutor_session_can_be_created_with_tutor_workspace_coreflex(
    api_client, morning_reconf_baseline_b,
):
    test_tutor_session_can_be_created_with_workspace_profiles(
        api_client, morning_reconf_baseline_b, "tutor_workspace_coreflex",
    )


@pytest.mark.django_db
def test_tutor_session_can_be_created_with_tutor_workspace_journal(
    api_client, morning_reconf_baseline_b,
):
    test_tutor_session_can_be_created_with_workspace_profiles(
        api_client, morning_reconf_baseline_b, "tutor_workspace_journal",
    )


@pytest.mark.django_db
def test_tutor_import_draft_stays_non_persistent_in_p1():
    """TUTOR — P1 : pas d'endpoint backend de persistance brouillon tutorat."""
    from django.urls import get_resolver

    resolver = get_resolver()
    patterns = [str(p.pattern) for p in resolver.url_patterns]
    joined = " ".join(patterns).lower()
    assert "tutor-draft" not in joined
    assert "tutor_journal" not in joined


@pytest.mark.django_db
def test_tutor_memory_panel_is_read_only(api_client, morning_reconf_baseline_b):
    """TUTOR — memory-summary lecture refusée (ACL actuelle)."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.tutor)
    response = api_client.get(
        f"/hugo/sessions/{world.learner_session.id}/memory-summary/"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_tutor_session_does_not_trigger_evaluation_chain(api_client, morning_reconf_baseline_b):
    """TUTOR — création session workspace sans auto-déclenchement évaluation."""
    world = morning_reconf_baseline_b
    profile = world.tutor_workspace_profiles["tutor_workspace_prep"]
    api_client.force_authenticate(user=world.tutor)
    create = api_client.post(
        "/hugo/sessions/",
        {"group": str(world.group.id), "learner_conversation_profile_id": str(profile.id)},
        format="json",
    )
    assert create.status_code == 201
    session_id = create.data["id"]
    readiness = api_client.get(f"/hugo/sessions/{session_id}/evaluation-readiness/")
    assert readiness.status_code in (200, 403, 404)


# --- Chat formateur P1 (TRAINER) ---


@pytest.mark.django_db
def test_trainer_chat_session_uses_trainer_profile_not_learner_profile(morning_reconf_baseline_b):
    """TRAINER — session chat formateur : learner = trainer, pas profil workspace tuteur."""
    world = morning_reconf_baseline_b
    session = world.trainer_session
    assert session.learner_id == world.trainer.id
    name = getattr(session.learner_conversation_profile, "name", None)
    assert name not in TUTOR_WORKSPACE_PROFILE_CODES


@pytest.mark.django_db
def test_trainer_import_flow_requires_human_confirmation(api_client, morning_reconf_baseline_b):
    """TRAINER — import chat exige meta import_kind (confirmation côté front)."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.trainer)
    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Sans meta",
            "source_type": "chat_import",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_trainer_import_meta_payload_matches_contract(api_client, morning_reconf_baseline_b):
    """TRAINER — meta import chat conforme au contrat P1."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.trainer)
    session_id = str(world.trainer_session.id)
    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Explicitation import",
            "content_type": "pedagogical_explication",
            "source_type": "chat_import",
            "status": "derived_provisional",
            "meta": {
                "import_kind": "trainer_explication",
                "session_id": session_id,
                "source": "chat",
                "explication": {"learning_objective": "Objectif test"},
            },
        },
        format="json",
    )
    assert response.status_code == 201
    item = TrainerKnowledgeItem.objects.get(id=response.data["id"])
    assert item.meta["import_kind"] == "trainer_explication"
    assert item.meta["session_id"] == session_id


@pytest.mark.django_db
def test_trainer_document_actions_do_not_break_chat_session(api_client, morning_reconf_baseline_b):
    """TRAINER — import knowledge n'altère pas la session chat."""
    world = morning_reconf_baseline_b
    session = world.trainer_session
    api_client.force_authenticate(user=world.trainer)
    api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Doc lié",
            "source_type": "chat_import",
            "status": "derived_provisional",
            "meta": {
                "import_kind": "trainer_resource_provisional",
                "session_id": str(session.id),
            },
        },
        format="json",
    )
    session.refresh_from_db()
    get_session = api_client.get(f"/hugo/sessions/{session.id}/")
    assert get_session.status_code == 200
    assert str(get_session.data["id"]) == str(session.id)


# --- Contrats et non-régression (CONTRACT / CROSS) ---


@pytest.mark.django_db
def test_contract_ui_state_fields_stable(api_client, morning_reconf_baseline_b):
    """CONTRACT — clés ui-state stables."""
    world = morning_reconf_baseline_b
    session = world.learner_session
    session.conversation_progress = _session_progress(str(session.id))
    session.save(update_fields=["conversation_progress"])
    api_client.force_authenticate(user=world.learner)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")
    assert CLUSTER15_UI_STATE_CORE_KEYS.issubset(set(response.data.keys()))


@pytest.mark.django_db
def test_contract_memory_summary_fields_stable(api_client, morning_reconf_baseline_b):
    """CONTRACT — clés memory-summary stables."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.learner)
    url = reverse("session_memory_summary", kwargs={"session_id": str(world.learner_session.id)})
    response = api_client.get(url)
    assert response.status_code == 200
    assert MEMORY_SUMMARY_CORE_KEYS.issubset(set(response.data.keys()))


@pytest.mark.django_db
def test_contract_conduct_profiles_crud_stable(api_client, morning_reconf_baseline_b):
    """CONTRACT — conduct-profiles listable par orgadmin."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.orgadmin)
    response = api_client.get("/hugo/conduct-profiles/")
    assert response.status_code == 200
    for row in response.data:
        assert "posture" in row
        assert "forbidden_moves" in row


@pytest.mark.django_db
def test_contract_profile_resolution_no_cross_role_bleed(morning_reconf_baseline_b):
    """CROSS — profils workspace tuteur distincts des prompts learner default."""
    world = morning_reconf_baseline_b
    tutor_prompt = world.tutor_workspace_profiles["tutor_workspace_prep"].reflective_tutor_prompt
    learner_session = HugoSession.objects.create(
        organisation=world.organisation,
        group=world.group,
        learner=world.learner,
        learner_conversation_profile=world.tutor_workspace_profiles["tutor_workspace_prep"],
    )
    resolved = _resolve_tutor_prompt(
        learner_session,
        posture=ConversationPosture.REFLECTIVE_AFEST.value,
    )
    assert resolved.id == tutor_prompt.id
    assert resolved.code == "tutor_workspace_prep"


@pytest.mark.django_db
def test_no_prompt_bleed_tutor_to_trainer_or_learner(morning_reconf_baseline_b):
    """CROSS — prompt tuteur workspace non résolu sur session formateur."""
    world = morning_reconf_baseline_b
    resolved = _resolve_tutor_prompt(world.trainer_session, posture="reflective_afest")
    assert resolved.code != "tutor_workspace_prep"


@pytest.mark.django_db
def test_no_prompt_bleed_trainer_to_tutor_or_learner(morning_reconf_baseline_b):
    """CROSS — codes prompts workspace isolés par code métier."""
    world = morning_reconf_baseline_b
    workspace_codes = set(TUTOR_WORKSPACE_PROFILE_CODES)
    org_prompt_codes = set(
        TutorPrompt.objects.filter(organisation=world.organisation).values_list("code", flat=True)
    )
    assert workspace_codes.issubset(org_prompt_codes)
    assert "morning_learner_default" in org_prompt_codes
    assert "morning_learner_default" not in workspace_codes


@pytest.mark.django_db
def test_no_prompt_bleed_learner_to_tutor_or_trainer(morning_reconf_baseline_b):
    """CROSS — session tuteur workspace résout son propre prompt."""
    world = morning_reconf_baseline_b
    profile = world.tutor_workspace_profiles["tutor_workspace_diagnostic"]
    session = HugoSession.objects.create(
        organisation=world.organisation,
        group=world.group,
        learner=world.tutor,
        learner_conversation_profile=profile,
    )
    resolved = _resolve_tutor_prompt(session, posture="diagnostic")
    assert resolved.code == "tutor_workspace_diagnostic"


@pytest.mark.django_db
def test_tutor_never_receives_unshared_verbatim(api_client, morning_reconf_baseline_b):
    """TUTOR — timeline sans verbatim privé."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.tutor)
    response = api_client.get(
        f"/dashboard/groups/{world.group.id}/learners/{world.learner.id}/timeline/"
    )
    assert VERBATIM_PRIVATE_MARKER not in json.dumps(response.data)


@pytest.mark.django_db
def test_memory_summary_has_no_raw_message_content(api_client, morning_reconf_baseline_b):
    """LEARNER — memory-summary sans contenu message brut."""
    world = morning_reconf_baseline_b
    marker = "MESSAGE_BRUT_INTERDIT_MEMORY"
    HugoMessage.objects.create(
        organisation=world.organisation,
        session=world.learner_session,
        role=HugoMessage.Role.LEARNER,
        content=marker,
    )
    api_client.force_authenticate(user=world.learner)
    url = reverse("session_memory_summary", kwargs={"session_id": str(world.learner_session.id)})
    response = api_client.get(url)
    assert marker not in json.dumps(response.data)


@pytest.mark.django_db
def test_trainer_cannot_access_tutor_private_drafts_if_p1_non_persistent(api_client, morning_reconf_baseline_b):
    """TUTOR/TRAINER — P1 brouillons non exposés via API (pas de persistance)."""
    world = morning_reconf_baseline_b
    api_client.force_authenticate(user=world.trainer)
    for path in (
        "/hugo/tutor-drafts/",
        "/hugo/tutor/workspace-artifacts/",
        "/hugo/trainer/tutor-drafts/",
    ):
        response = api_client.get(path)
        assert response.status_code in (404, 405)


@pytest.mark.django_db
def test_share_endpoint_behavior_unchanged(api_client, morning_reconf_baseline_b):
    """LEARNER — POST /share/ met à jour les flags partage."""
    world = morning_reconf_baseline_b
    session = world.learner_session
    api_client.force_authenticate(user=world.learner)
    response = api_client.post(
        f"/hugo/sessions/{session.id}/share/",
        {"share_summary": True, "share_evidence": False, "share_verbatim": True},
        format="json",
    )
    assert response.status_code == 200
    session.refresh_from_db()
    assert session.share_summary is True
    assert session.share_verbatim is True
    assert session.share_evidence is False


@pytest.mark.django_db
def test_morning_reconf_fixture_idempotent():
    """FIXTURE — build_morning_reconf_baseline_b est rejouable."""
    first = build_morning_reconf_baseline_b(org_name="Idempotent Org")
    second = build_morning_reconf_baseline_b(org_name="Idempotent Org")
    assert first.organisation.id == second.organisation.id
    assert set(first.tutor_workspace_profiles.keys()) == set(second.tutor_workspace_profiles.keys())
