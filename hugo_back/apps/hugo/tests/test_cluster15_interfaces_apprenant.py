"""Cluster 15 — tests API interfaces apprenant (personae A1, A2, A3).

Couvre : posture (set-posture), learner_display_profile, contrat UIState unique,
CTA synthèse/évaluation, memory-summary intra-conversation.

Exécution locale :
  cd hugo_back && python -m pytest apps/hugo/tests/test_cluster15_interfaces_apprenant.py -v
"""
from __future__ import annotations

import json

import pytest

from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import EvaluationPolicy, HugoMessage, HugoSession

# --- Entrées campagne (renseigner pour captures UI manuelles) ---
ENVIRONMENT = "local"
BRANCH = "feature/cluster15-interfaces-apprenant-formateur"
SESSION_IDS_DEMO = [
    "00000000-0000-4000-8000-000000000001",  # A1 youth — remplacer par session démo réelle
    "00000000-0000-4000-8000-000000000002",  # A2 adult
    "00000000-0000-4000-8000-000000000003",  # A3 professional
]

CLUSTER15_UI_STATE_CORE_KEYS = {
    "scene_label",
    "scene_progress",
    "maturity_color",
    "conversation_mode",
    "learner_display_profile",
    "gamification_profile",
    "cta_synthesis",
    "cta_evaluation",
}

CONVERSATION_MODE_KEYS = {
    "code",
    "label",
    "can_switch",
    "switch_warning",
    "allowed_posture_transitions",
    "switch_locked_reason",
}
CTA_UI_KEYS = {"button_label", "button_disabled", "helper_text"}
CTA_EVALUATION_UI_KEYS = CTA_UI_KEYS | {"advisory"}

P0_FORBIDDEN_IN_UI = set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS) | {
    "turn_state",
    "conversation_decision",
    "episode_clarity",
    "cognitive_load",
    "interaction_risk",
}

VERBATIM_MARKER = "CLUSTER15_MEMORY_VERBATIM_DO_NOT_EXPOSE"


def _base_progress(*, posture: str = "reflective_afest", maturity: str = "orange") -> dict:
    return {
        "session_id": "pending",
        "posture": posture,
        "active_branches": [],
        "active_branches_count": 0,
        "overall_maturity": maturity,
        "synthesis_eligible": maturity in {"orange", "green"},
        "evaluation_eligible": maturity == "green",
        "missing_for_next_level": [],
        "reason_codes": [],
    }


def _create_session(
    *,
    organisation,
    learner_user,
    group,
    posture: str = "reflective_afest",
    maturity: str = "orange",
    **session_kwargs,
) -> HugoSession:
    progress = _base_progress(posture=posture, maturity=maturity)
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture=posture,
        conversation_progress=progress,
        **session_kwargs,
    )
    progress["session_id"] = str(session.id)
    session.conversation_progress = progress
    session.save(update_fields=["conversation_progress"])
    return session


def _get_ui_state(api_client, session_id: str, **query_params):
    return api_client.get(f"/hugo/sessions/{session_id}/ui-state/", query_params)


# ---------------------------------------------------------------------------
# PERSONA A1 — Karim (youth) — posture, profil, mémoire, CTA
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_a1_youth_ui_state_exposes_display_profile_and_conversation_mode(
    api_client, learner_user, organisation, group
):
    """A1 — learner_display_profile=youth (groupe) + conversation_mode cohérent."""
    group.learner_display_profile = "youth"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        posture="diagnostic",
    )

    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(api_client, session.id)

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == "youth"
    mode = response.data["conversation_mode"]
    assert set(mode.keys()) == CONVERSATION_MODE_KEYS
    assert mode["code"] == "diagnostic"
    assert mode["label"] == "Diagnostic"


@pytest.mark.django_db
def test_a1_set_posture_allowed_transition_returns_200_and_updates_session(
    api_client, learner_user, organisation, group
):
    """A1 — POST set-posture transition autorisée (reflective → diagnostic) → 200."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        posture="reflective_afest",
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.post(
        f"/hugo/sessions/{session.id}/set-posture/",
        {"posture": "diagnostic"},
        format="json",
    )
    session.refresh_from_db()

    assert response.status_code == 200
    assert response.data["posture"] == "diagnostic"
    assert session.posture == "diagnostic"
    assert session.conversation_profile_override == "diagnostic"


@pytest.mark.django_db
def test_a1_set_posture_forbidden_transition_returns_400(
    api_client, learner_user, organisation, group
):
    """A1 — POST set-posture transition interdite (diagnostic → knowledge_review) → 400."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        posture="diagnostic",
        maturity="red",
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.post(
        f"/hugo/sessions/{session.id}/set-posture/",
        {"posture": "knowledge_review"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["detail"] == "transition_not_allowed"


@pytest.mark.django_db
def test_a1_memory_summary_intra_conversation_without_verbatim(
    api_client, learner_user, organisation, group
):
    """A1 — memory-summary gouverné sans verbatim brut (oracle A1-05 cluster 15)."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content=VERBATIM_MARKER,
        llm_request_payload={
            "turn_state": {
                "covered_points": ["point_stabilise_a1"],
                "remaining_open_points": ["point_ouvert_a1"],
            }
        },
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/memory-summary/")

    assert response.status_code == 200
    session_memory = response.data["session_memory"]
    assert session_memory["memory_scope"] == "intra_conversation"
    assert session_memory["session_id"] == str(session.id)
    assert "point_stabilise_a1" in json.dumps(session_memory)
    assert VERBATIM_MARKER not in json.dumps(response.data)


@pytest.mark.django_db
def test_a1_cta_synthesis_and_evaluation_contract_when_orange(
    api_client, learner_user, organisation, group
):
    """A1 — CTA synthèse/évaluation cohérents avec maturité ORANGE."""
    group.learner_display_profile = "youth"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        maturity="orange",
    )
    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(api_client, session.id)

    assert response.status_code == 200
    synth = response.data["cta_synthesis"]
    eval_cta = response.data["cta_evaluation"]
    assert set(synth["ui"].keys()) >= CTA_UI_KEYS
    assert set(eval_cta["ui"].keys()) >= CTA_EVALUATION_UI_KEYS
    assert synth["synthesis_ready_status"] == "eligible"
    assert eval_cta["evaluation_ready_status"] in {
        "eligible",
        "blocked_not_enough_content",
        "blocked_context_incomplete",
        "blocked_missing_data",
        "blocked_min_turns_not_reached",
        "blocked_other",
    }


# ---------------------------------------------------------------------------
# PERSONA A2 — Nadège (adult) — contrat UIState + profil adult
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_a2_adult_ui_state_shares_same_core_contract_as_a1(
    api_client, learner_user, organisation, group
):
    """A2 — même contrat UIState que A1/A3 ; seul learner_display_profile diffère."""
    group.learner_display_profile = "adult"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
    )
    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(api_client, session.id)

    assert response.status_code == 200
    assert CLUSTER15_UI_STATE_CORE_KEYS.issubset(set(response.data.keys()))
    assert response.data["learner_display_profile"] == "adult"
    assert set(response.data["conversation_mode"].keys()) == CONVERSATION_MODE_KEYS


@pytest.mark.django_db
def test_a2_adult_display_profile_independent_from_gamification_profile(
    api_client, learner_user, organisation, group
):
    """A2 — learner_display_profile=adult distinct de gamification_profile."""
    group.learner_display_profile = "youth"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
    )
    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(
        api_client,
        session.id,
        gamification_profile="C",
        learner_display_profile="adult",
    )

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == "adult"
    assert response.data["gamification_profile"] == "C"


@pytest.mark.django_db
def test_a2_ui_state_after_set_posture_reflects_new_conversation_mode(
    api_client, learner_user, organisation, group
):
    """A2 — après set-posture, ui-state.conversation_mode.code aligné sur session.posture."""
    group.learner_display_profile = "adult"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        posture="reflective_afest",
    )
    api_client.force_authenticate(user=learner_user)
    post = api_client.post(
        f"/hugo/sessions/{session.id}/set-posture/",
        {"posture": "knowledge_review"},
        format="json",
    )
    assert post.status_code == 200

    ui = _get_ui_state(api_client, session.id)
    assert ui.status_code == 200
    assert ui.data["conversation_mode"]["code"] == "knowledge_review"
    assert ui.data["conversation_mode"]["label"] == "Savoirs / révision"


@pytest.mark.django_db
def test_a2_memory_summary_exposes_structured_fields_not_raw_thread(
    api_client, learner_user, organisation, group
):
    """A2 — memory-summary : champs structurés session_memory, pas de clé turn_state."""
    group.learner_display_profile = "adult"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Je travaille sur un geste infirmier difficile.",
        llm_request_payload={"turn_state": {"covered_points": ["geste_identifie"]}},
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/memory-summary/")

    assert response.status_code == 200
    memory = response.data["session_memory"]
    assert "memory_scope" in memory
    assert "turn_state" not in memory
    assert "turn_state" not in json.dumps(memory).lower()


# ---------------------------------------------------------------------------
# PERSONA A3 — Ibrahima (professional) — CTA + profil professional
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_a3_professional_default_display_profile_and_cta_green_eligible(
    api_client, learner_user, organisation, group
):
    """A3 — profil professional (défaut) + CTA évaluation eligible en GREEN."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        maturity="green",
    )
    progress = dict(session.conversation_progress)
    progress["active_branches"] = [
        {
            "branch_id": "b-pro",
            "theme_label": "Diagnostic technique",
            "objective_label": "Clôture",
            "exploration_level": "green",
            "is_active": True,
            "reason_codes": [],
        }
    ]
    progress["active_branches_count"] = 1
    progress["evaluation_eligible"] = True
    progress["reason_codes"] = ["evaluation_eligible"]
    session.conversation_progress = progress
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(api_client, session.id)

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == "professional"
    eval_cta = response.data["cta_evaluation"]
    assert eval_cta["evaluation_ready_status"] == "eligible"
    assert eval_cta["ui"]["button_disabled"] is False


@pytest.mark.django_db
def test_a3_cta_synthesis_blocked_when_red_regardless_of_display_profile(
    api_client, learner_user, organisation, group
):
    """A3 — CTA synthèse bloquée en RED ; indépendant du profil d'affichage."""
    group.learner_display_profile = "professional"
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        maturity="red",
    )
    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(api_client, session.id)

    assert response.status_code == 200
    synth = response.data["cta_synthesis"]
    assert synth["synthesis_ready_status"] != "eligible"
    assert synth["ui"]["button_disabled"] is True


@pytest.mark.django_db
def test_a3_request_evaluation_endpoint_respects_cta_eligibility(
    api_client, learner_user, organisation, group
):
    """A3 — POST request-evaluation → 400 si non eligible (aligné cta_evaluation)."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        maturity="red",
    )
    policy, _ = EvaluationPolicy.objects.get_or_create(
        organisation=organisation,
        group=group,
        defaults={"allow_early_trigger": True},
    )
    policy.allow_early_trigger = False
    policy.save(update_fields=["allow_early_trigger", "updated_at"])

    api_client.force_authenticate(user=learner_user)
    ui = _get_ui_state(api_client, session.id)
    assert ui.data["cta_evaluation"]["evaluation_ready_status"] != "eligible"

    response = api_client.post(
        f"/hugo/sessions/{session.id}/request-evaluation/",
        {},
        format="json",
    )
    assert response.status_code == 400
    assert response.data["error"] == "evaluation_not_eligible"


@pytest.mark.django_db
def test_a3_ui_state_surface_has_no_p0_fields_across_profiles(
    api_client, learner_user, organisation, group
):
    """A3 — contrat UIState sans fuite P0 (oracle INV-01, profil professional)."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        posture="knowledge_review",
        maturity="red",
    )
    api_client.force_authenticate(user=learner_user)
    response = _get_ui_state(api_client, session.id)

    assert response.status_code == 200
    assert set(response.data.keys()).isdisjoint(P0_FORBIDDEN_IN_UI)
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    for token in ("turn_state", "episode_clarity", "cognitive_load"):
        assert token not in serialized
