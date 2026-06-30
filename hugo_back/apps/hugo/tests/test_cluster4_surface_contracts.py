"""Cluster 4 — contrats de surface UIState (conversation_mode, learner_display_profile)."""
import json
import re

import pytest

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import HugoSession
from apps.hugo.services.ui_state_builder import (
    LEARNER_DISPLAY_PROFILE_VALUES,
    _build_conversation_mode,
    normalize_learner_display_profile,
)
from apps.hugo.services.conversation_progress_calculator import build_conversation_progress_contract
from types import SimpleNamespace


P0_PATTERN = re.compile(
    r"episode_clarity|cognitive_load|interaction_risk|problem_salience|reflection_phase|turn_state|\bp0\b",
    re.IGNORECASE,
)

CONVERSATION_MODE_KEYS = {
    "code",
    "label",
    "can_switch",
    "switch_warning",
    "allowed_posture_transitions",
    "switch_locked_reason",
}


@pytest.mark.django_db
def test_ui_state_exposes_conversation_mode_from_session_posture(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="diagnostic",
        conversation_progress={
            "session_id": "pending",
            "posture": "diagnostic",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "orange",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")

    assert response.status_code == 200
    mode = response.data["conversation_mode"]
    assert set(mode.keys()) == CONVERSATION_MODE_KEYS
    assert mode["code"] == "diagnostic"
    assert mode["label"] == "Diagnostic"
    assert mode["can_switch"] is True
    assert mode["switch_warning"] in (None, "")


@pytest.mark.django_db
def test_ui_state_exposes_learner_display_profile_default(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == "professional"


@pytest.mark.parametrize("profile", sorted(LEARNER_DISPLAY_PROFILE_VALUES))
@pytest.mark.django_db
def test_ui_state_accepts_learner_display_profile_query_param(
    api_client, learner_user, organisation, group, profile
):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(
        f"/hugo/sessions/{session.id}/ui-state/?learner_display_profile={profile}"
    )

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == profile


@pytest.mark.django_db
def test_ui_state_gamification_and_display_profile_are_independent(
    api_client, learner_user, organisation, group
):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(
        f"/hugo/sessions/{session.id}/ui-state/?gamification_profile=C&learner_display_profile=youth"
    )

    assert response.status_code == 200
    assert response.data["gamification_profile"] == "C"
    assert response.data["learner_display_profile"] == "youth"


@pytest.mark.django_db
def test_ui_state_surface_fields_do_not_leak_p0(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="knowledge_review",
        conversation_progress={
            "session_id": "pending",
            "posture": "knowledge_review",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")

    assert response.status_code == 200
    top_keys = set(response.data.keys())
    assert top_keys.isdisjoint(set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS))
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    assert not P0_PATTERN.search(serialized)
    assert "conversation_mode" in response.data
    assert "learner_display_profile" in response.data


def test_build_conversation_mode_knowledge_review_red_sets_switch_warning():
    progress = build_conversation_progress_contract(
        session_id="s1",
        turn_state=SimpleNamespace(
            conversation_goal="Réviser",
            current_phase="exploration",
            covered_points=[],
            remaining_open_points=["point"],
            episode_clarity="low",
            has_concrete_actions=False,
            loop_risk="low",
            cognitive_load="low",
            interaction_risk="low",
        ),
        decision=SimpleNamespace(),
        posture=ConversationPosture.KNOWLEDGE_REVIEW,
    )
    mode = _build_conversation_mode(progress)

    assert mode["code"] == "knowledge_review"
    assert mode["label"] == "Savoirs / révision"
    assert mode["can_switch"] is True
    assert mode["switch_warning"]


def test_normalize_learner_display_profile_falls_back_to_professional():
    assert normalize_learner_display_profile(None) == "professional"
    assert normalize_learner_display_profile("invalid") == "professional"
    assert normalize_learner_display_profile("youth") == "youth"


@pytest.mark.django_db
def test_ui_state_uses_group_learner_display_profile_by_default(api_client, learner_user, organisation, group):
    group.learner_display_profile = "youth"
    group.save(update_fields=["learner_display_profile"])

    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == "youth"


@pytest.mark.django_db
def test_ui_state_query_param_overrides_group_learner_display_profile(
    api_client, learner_user, organisation, group
):
    group.learner_display_profile = "youth"
    group.save(update_fields=["learner_display_profile"])

    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(
        f"/hugo/sessions/{session.id}/ui-state/?learner_display_profile=adult"
    )

    assert response.status_code == 200
    assert response.data["learner_display_profile"] == "adult"
