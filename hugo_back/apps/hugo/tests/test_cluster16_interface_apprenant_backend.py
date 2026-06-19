"""Cluster 16 — protocole tests interface apprenant conforme spec 2.0.

Référence : docs-workspace/cluster16_protocole_tests_interface_apprenant_v1.md

Exécution :
  cd hugo_back && python -m pytest apps/hugo/tests/test_cluster16_interface_apprenant_backend.py -v
"""
from __future__ import annotations

import json
import re

import pytest

from apps.hugo.domain.conversation_profile import ConversationPosture, deserialize_conversation_progress
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import EvaluationPolicy, HugoMessage, HugoSession
from apps.hugo.services.ui_state_builder import _build_conversation_mode

ENVIRONMENT = "local"
BRANCH = "feature/cluster16-interface-apprenant-spec-2-0"

SESSION_IDS_DEMO = {
    "youth": "00000000-0000-4000-8000-000000000011",
    "adult": "00000000-0000-4000-8000-000000000012",
    "professional": "00000000-0000-4000-8000-000000000013",
}

CONVERSATION_MODE_KEYS = {
    "code",
    "label",
    "can_switch",
    "switch_warning",
    "allowed_posture_transitions",
    "switch_locked_reason",
}
TRANSITION_ENTRY_KEYS = {"code", "label", "allowed", "warning"}

EVALUATION_READY_STATUSES = {
    "eligible",
    "blocked_missing_data",
    "blocked_min_turns_not_reached",
    "blocked_context_incomplete",
    "blocked_other",
}
SYNTHESIS_READY_STATUSES = {
    "eligible",
    "blocked_not_enough_content",
    "blocked_context_incomplete",
}

DISPLAY_PROFILE_VALUES = {"youth", "adult", "professional"}
CTA_SYNTHESIS_UI_KEYS = {"button_label", "button_disabled", "helper_text", "show_synthesis_button"}
CTA_EVALUATION_UI_KEYS = {"button_label", "button_disabled", "helper_text", "show_evaluation_button", "advisory"}

P0_FORBIDDEN_IN_UI = set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS) | {
    "turn_state",
    "conversation_decision",
    "episode_clarity",
    "cognitive_load",
    "interaction_risk",
}
P0_PATTERN = re.compile(
    r"episode_clarity|cognitive_load|interaction_risk|problem_salience|reflection_phase|turn_state|\bp0\b",
    re.IGNORECASE,
)

SESSION_MEMORY_REQUIRED_KEYS = {
    "theme",
    "learning_objective",
    "facts_confirmed",
    "open_points",
    "pending_actions",
    "memory_scope",
    "session_id",
}

VERBATIM_MARKER = "CLUSTER16_MEMORY_VERBATIM_DO_NOT_EXPOSE"


def _minimal_progress(**overrides) -> dict:
    base = {
        "session_id": "pending",
        "posture": "reflective_afest",
        "active_branches": [],
        "active_branches_count": 0,
        "overall_maturity": "orange",
        "synthesis_eligible": True,
        "evaluation_eligible": False,
        "missing_for_next_level": [],
        "reason_codes": [],
        "dispersion_risk": False,
        "priority_branch_id": None,
    }
    base.update(overrides)
    return base


def _create_session(*, organisation, learner_user, group, progress: dict | None = None, **kwargs) -> HugoSession:
    payload = _minimal_progress(**(progress or {}))
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture=payload["posture"],
        conversation_progress=payload,
        **kwargs,
    )
    payload["session_id"] = str(session.id)
    session.conversation_progress = payload
    session.save(update_fields=["conversation_progress"])
    return session


def _ui_state(api_client, session_id):
    return api_client.get(f"/hugo/sessions/{session_id}/ui-state/")


# ---------------------------------------------------------------------------
# B16-P — posture / mode
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_b16_p1_ui_state_conversation_mode_present_without_p0(api_client, learner_user, organisation, group):
    """B16-P1 — conversation_mode présent, labels cohérents, aucune fuite P0."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={"posture": "diagnostic", "overall_maturity": "red"},
    )
    api_client.force_authenticate(user=learner_user)
    response = _ui_state(api_client, session.id)

    assert response.status_code == 200
    top_keys = set(response.data.keys())
    assert top_keys.isdisjoint(P0_FORBIDDEN_IN_UI)
    mode = response.data["conversation_mode"]
    assert set(mode.keys()) == CONVERSATION_MODE_KEYS
    assert mode["code"] in {p.value for p in ConversationPosture}
    assert mode["label"]
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    assert not P0_PATTERN.search(serialized)


@pytest.mark.django_db
def test_b16_p1_allowed_posture_transitions_shape(api_client, learner_user, organisation, group):
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={"posture": "diagnostic", "overall_maturity": "red"},
    )
    api_client.force_authenticate(user=learner_user)
    transitions = _ui_state(api_client, session.id).data["conversation_mode"]["allowed_posture_transitions"]

    assert len(transitions) == 2
    for entry in transitions:
        assert set(entry.keys()) == TRANSITION_ENTRY_KEYS
        assert entry["code"] in {p.value for p in ConversationPosture if p.value != "diagnostic"}


@pytest.mark.django_db
def test_b16_p2_set_posture_valid_updates_ui_state(api_client, learner_user, organisation, group):
    """B16-P2 — bascule autorisée : 200 + UIState aligné."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={"posture": "reflective_afest", "overall_maturity": "orange"},
    )
    api_client.force_authenticate(user=learner_user)
    post = api_client.post(
        f"/hugo/sessions/{session.id}/set-posture/",
        {"posture": "diagnostic"},
        format="json",
    )
    assert post.status_code == 200
    assert post.data["posture"] == "diagnostic"

    ui = _ui_state(api_client, session.id).data
    assert ui["conversation_mode"]["code"] == "diagnostic"
    assert ui["conversation_mode"]["label"] == "Diagnostic"


@pytest.mark.django_db
def test_b16_p3_set_posture_refused_keeps_ui_state_coherent(api_client, learner_user, organisation, group):
    """B16-P3 — bascule refusée : 400 propre, UIState inchangé."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={"posture": "diagnostic", "overall_maturity": "red"},
    )
    api_client.force_authenticate(user=learner_user)
    before = _ui_state(api_client, session.id).data["conversation_mode"]["code"]

    response = api_client.post(
        f"/hugo/sessions/{session.id}/set-posture/",
        {"posture": "knowledge_review"},
        format="json",
    )
    assert response.status_code == 400
    assert response.data["detail"] == "transition_not_allowed"
    assert "turn_state" not in json.dumps(response.data).lower()
    assert "episode_clarity" not in json.dumps(response.data).lower()

    after = _ui_state(api_client, session.id).data["conversation_mode"]["code"]
    assert after == before == "diagnostic"


@pytest.mark.django_db
def test_b16_p3_switch_locked_reason_when_no_transitions_allowed(monkeypatch):
    from apps.hugo.services import ui_state_builder

    monkeypatch.setattr(
        ui_state_builder,
        "can_transition",
        lambda *args, **kwargs: (False, "transition_not_allowed"),
    )
    progress = deserialize_conversation_progress(
        {"session_id": "s1", "posture": "reflective_afest", "overall_maturity": "green"}
    )
    mode = _build_conversation_mode(progress)
    assert mode["can_switch"] is False
    assert mode["switch_locked_reason"]


# ---------------------------------------------------------------------------
# B16-C — CTA synthèse / évaluation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_b16_c1_cta_contracts_main_fields(api_client, learner_user, organisation, group):
    """B16-C1 — CTA synthèse/évaluation : enums, blocking_reasons, endpoints, ui.*."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={
            "overall_maturity": "orange",
            "evaluation_eligible": False,
            "synthesis_eligible": True,
            "missing_for_next_level": ["Nommer une action concrète."],
            "reason_codes": ["evaluation_blocked_maturity"],
        },
    )
    api_client.force_authenticate(user=learner_user)
    data = _ui_state(api_client, session.id).data

    synth = data["cta_synthesis"]
    eval_cta = data["cta_evaluation"]
    assert synth["synthesis_ready_status"] in SYNTHESIS_READY_STATUSES
    assert eval_cta["evaluation_ready_status"] in EVALUATION_READY_STATUSES
    assert isinstance(synth["blocking_reasons"], list)
    assert isinstance(eval_cta["blocking_reasons"], list)
    assert synth["endpoints"]["request_synthesis"].endswith("request-synthesis/")
    assert eval_cta["endpoints"]["request_evaluation"].endswith("request-evaluation/")
    assert set(synth["ui"].keys()) >= CTA_SYNTHESIS_UI_KEYS
    assert set(eval_cta["ui"].keys()) >= CTA_EVALUATION_UI_KEYS
    for reason in synth["blocking_reasons"] + eval_cta["blocking_reasons"]:
        assert isinstance(reason, str)
        assert not P0_PATTERN.search(reason)


@pytest.mark.django_db
def test_b16_c2_evaluation_advisory_eligible_with_helper(api_client, learner_user, organisation, group):
    """B16-C2 — évaluation déconseillée mais possible : eligible + advisory + helper_text."""
    EvaluationPolicy.objects.update_or_create(
        organisation=organisation,
        group=group,
        defaults={"allow_early_trigger": True},
    )
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={
            "overall_maturity": "orange",
            "evaluation_eligible": False,
            "synthesis_eligible": True,
            "missing_for_next_level": ["Nommer une action concrète déjà réalisée."],
            "reason_codes": ["evaluation_blocked_maturity"],
        },
    )
    api_client.force_authenticate(user=learner_user)
    cta = _ui_state(api_client, session.id).data["cta_evaluation"]

    assert cta["evaluation_ready_status"] == "eligible"
    assert cta["ui"]["advisory"] is True
    assert cta["ui"]["button_disabled"] is False
    assert cta["ui"]["helper_text"]
    for reason in cta["blocking_reasons"]:
        assert not P0_PATTERN.search(reason)


@pytest.mark.django_db
def test_b16_c2_evaluation_not_advisory_when_fully_eligible(api_client, learner_user, organisation, group):
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={
            "overall_maturity": "green",
            "evaluation_eligible": True,
            "synthesis_eligible": True,
            "reason_codes": ["evaluation_eligible"],
        },
    )
    api_client.force_authenticate(user=learner_user)
    cta = _ui_state(api_client, session.id).data["cta_evaluation"]

    assert cta["evaluation_ready_status"] == "eligible"
    assert cta["ui"]["advisory"] is False
    assert cta["ui"]["button_label"] == "Demander une évaluation"


# ---------------------------------------------------------------------------
# B16-M — mémoire session_memory
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_b16_m1_memory_summary_minimal_structure(api_client, learner_user, organisation, group):
    """B16-M1 — session_memory : champs minimaux + memory_scope intraconversation."""
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Je travaille sur un geste technique.",
        llm_request_payload={
            "turn_state": {
                "covered_points": ["geste_identifie"],
                "remaining_open_points": ["point_ouvert_c16"],
            }
        },
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/memory-summary/")

    assert response.status_code == 200
    memory = response.data["session_memory"]
    assert SESSION_MEMORY_REQUIRED_KEYS <= set(memory.keys())
    assert memory["memory_scope"] == "intra_conversation"
    assert memory["session_id"] == str(session.id)


@pytest.mark.django_db
def test_b16_m2_memory_summary_excludes_verbatim(api_client, learner_user, organisation, group):
    """B16-M2 — aucun verbatim brut dans session_memory."""
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
                "covered_points": ["point_stabilise_c16"],
                "remaining_open_points": [],
            }
        },
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/memory-summary/")
    serialized = json.dumps(response.data, ensure_ascii=False)

    assert VERBATIM_MARKER not in serialized
    assert "turn_state" not in serialized.lower()
    assert "point_stabilise_c16" in serialized


# ---------------------------------------------------------------------------
# B16-L — profils d'affichage
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("profile", sorted(DISPLAY_PROFILE_VALUES))
def test_b16_l1_learner_display_profile_enum_in_ui_state(
    api_client, learner_user, organisation, group, profile
):
    """B16-L1 — learner_display_profile enum fermé présent dans UIState."""
    group.learner_display_profile = profile
    group.save(update_fields=["learner_display_profile"])
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
    )
    api_client.force_authenticate(user=learner_user)
    data = _ui_state(api_client, session.id).data

    assert data["learner_display_profile"] == profile
    assert data["learner_display_profile"] in DISPLAY_PROFILE_VALUES


# ---------------------------------------------------------------------------
# B16-S — scène / branche / dispersion (UIState)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_b16_s1_ui_state_scene_dispersion_and_priority_branch(api_client, learner_user, organisation, group):
    session = _create_session(
        organisation=organisation,
        learner_user=learner_user,
        group=group,
        progress={
            "dispersion_risk": True,
            "priority_branch_id": "branch-main",
            "active_branches": [
                {
                    "branch_id": "branch-main",
                    "theme_label": "Sécurité chantier",
                    "objective_label": "Clarifier la procédure",
                    "exploration_level": "orange",
                    "is_active": True,
                    "reason_codes": [],
                }
            ],
            "active_branches_count": 1,
        },
    )
    api_client.force_authenticate(user=learner_user)
    data = _ui_state(api_client, session.id).data

    assert data["scene_label"]
    assert data["maturity_color"] in {"red", "orange", "green"}
    assert data["dispersion_risk"] is True
    assert data["priority_branch_label"] == "Sécurité chantier"


def test_b16_unit_conversation_mode_lists_non_current_postures():
    progress = deserialize_conversation_progress(
        {"session_id": "s1", "posture": "reflective_afest", "overall_maturity": "orange"}
    )
    mode = _build_conversation_mode(progress)
    codes = {entry["code"] for entry in mode["allowed_posture_transitions"]}
    assert codes == {"diagnostic", "knowledge_review"}
