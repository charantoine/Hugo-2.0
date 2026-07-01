"""Seed personas *_test_2 pour baseline B (sqlite_test) — idempotent."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.accounts.models import Organisation, Role
from apps.accounts.seeds import personas_test_2_constants as C
from apps.accounts.seeds.group_attachments import (
    ensure_group_membership,
    ensure_tutor_learner_link,
)
from apps.hugo.models import HugoMessage, HugoSession, Trace, TrainerKnowledgeItem
from apps.hugo.services.tutor_workspace_bootstrap import ensure_tutor_workspace_profiles
from apps.referentials.models import Group, TutorLearnerLink


@dataclass
class PersonasTest2Result:
    organisation_id: str
    group_primary_id: str
    group_secondary_id: str
    learner_a_id: str
    learner_b_id: str
    learner_session_a_id: str
    learner_session_b_id: str
    trainer_session_id: str
    trace_id: str
    tutor_workspace_profiles: dict[str, str]
    users: dict[str, str]
    created: dict[str, bool]


def _role_enum(role_name: str) -> str:
    return getattr(Role, role_name)


def _ensure_user(org, username: str, role_name: str):
    User = get_user_model()
    role = _role_enum(role_name)
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"organisation": org, "role": role},
    )
    if not created:
        user.organisation = org
        user.role = role
    user.set_password(C.DEMO_PASSWORD)
    user.is_active = True
    user.save()
    return user, created


@transaction.atomic
def run_personas_test_2_seed() -> PersonasTest2Result:
    org, org_created = Organisation.objects.get_or_create(name=C.ORG_NAME)
    created_flags: dict[str, bool] = {"organisation": org_created}

    users: dict[str, object] = {}
    for key, (username, role_name) in C.USERS.items():
        user, was_created = _ensure_user(org, username, role_name)
        users[key] = user
        created_flags[f"user_{key}"] = was_created

    group_primary, gp_created = Group.objects.get_or_create(
        organisation=org,
        name=C.GROUP_PRIMARY,
    )
    group_secondary, gs_created = Group.objects.get_or_create(
        organisation=org,
        name=C.GROUP_SECONDARY,
    )
    created_flags["group_primary"] = gp_created
    created_flags["group_secondary"] = gs_created

    staff_keys = ("superadmin", "orgadmin", "coordo", "trainer", "tutor", "learner_a", "learner_b")
    for key in staff_keys:
        ensure_group_membership(org, group_primary, users[key])

    ensure_group_membership(org, group_secondary, users["learner_b"])

    ensure_tutor_learner_link(org, group_primary, users["tutor"], users["learner_a"])
    created_flags["tutor_link_a"] = TutorLearnerLink.objects.filter(
        organisation_id=org.id,
        group=group_primary,
        tutor=users["tutor"],
        learner=users["learner_a"],
    ).exists()

    tutor_profiles = ensure_tutor_workspace_profiles(org)
    profile_ids = {code: str(p.id) for code, p in tutor_profiles.items()}

    prep_profile = tutor_profiles["tutor_workspace_prep"]

    session_a, sa_created = HugoSession.objects.get_or_create(
        organisation=org,
        learner=users["learner_a"],
        group=group_primary,
        defaults={
            "share_verbatim": True,
            "share_summary": True,
            "posture": "reflective_afest",
        },
    )
    if not sa_created:
        session_a.share_verbatim = True
        session_a.share_summary = True
        session_a.save(update_fields=["share_verbatim", "share_summary"])
    created_flags["session_learner_a"] = sa_created

    HugoMessage.objects.filter(session=session_a).delete()
    HugoMessage.objects.create(
        organisation=org,
        session=session_a,
        role=HugoMessage.Role.LEARNER,
        content=C.VERBATIM_SHARED,
    )
    HugoMessage.objects.create(
        organisation=org,
        session=session_a,
        role=HugoMessage.Role.ASSISTANT,
        content="Qu'avez-vous observé sur le terrain cette semaine ?",
    )

    session_b, sb_created = HugoSession.objects.get_or_create(
        organisation=org,
        learner=users["learner_b"],
        group=group_primary,
        defaults={"share_verbatim": False},
    )
    HugoMessage.objects.filter(session=session_b).delete()
    HugoMessage.objects.create(
        organisation=org,
        session=session_b,
        role=HugoMessage.Role.LEARNER,
        content=C.VERBATIM_PRIVATE,
    )
    created_flags["session_learner_b"] = sb_created

    trainer_session, ts_created = HugoSession.objects.get_or_create(
        organisation=org,
        learner=users["trainer"],
        group=group_primary,
    )
    HugoMessage.objects.filter(session=trainer_session).delete()
    HugoMessage.objects.create(
        organisation=org,
        session=trainer_session,
        role=HugoMessage.Role.ASSISTANT,
        content="Quelle ressource pédagogique souhaitez-vous formaliser ?",
    )
    created_flags["session_trainer"] = ts_created

    tutor_session, tu_created = HugoSession.objects.get_or_create(
        organisation=org,
        learner=users["tutor"],
        group=group_primary,
        defaults={"learner_conversation_profile": prep_profile},
    )
    if tutor_session.learner_conversation_profile_id != prep_profile.id:
        tutor_session.learner_conversation_profile = prep_profile
        tutor_session.save(update_fields=["learner_conversation_profile"])
    created_flags["session_tutor_workspace"] = tu_created

    trace, tr_created = Trace.objects.get_or_create(
        organisation=org,
        session=session_a,
        defaults={"payload_structured": {"source": "personas_test_2"}},
    )
    created_flags["trace_a"] = tr_created

    knowledge, ki_created = TrainerKnowledgeItem.objects.get_or_create(
        organisation=org,
        content="Savoir formateur test_2 — sécuriser le chantier",
        defaults={"status": "declared", "source_type": "manual"},
    )
    created_flags["knowledge_item"] = ki_created

    TrainerKnowledgeItem.objects.get_or_create(
        organisation=org,
        content="Explicitation test_2 — risque électrique",
        defaults={
            "status": "derived_provisional",
            "content_type": "pedagogical_explication",
            "source_type": "manual",
        },
    )

    return PersonasTest2Result(
        organisation_id=str(org.id),
        group_primary_id=str(group_primary.id),
        group_secondary_id=str(group_secondary.id),
        learner_a_id=str(users["learner_a"].id),
        learner_b_id=str(users["learner_b"].id),
        learner_session_a_id=str(session_a.id),
        learner_session_b_id=str(session_b.id),
        trainer_session_id=str(trainer_session.id),
        trace_id=str(trace.id),
        tutor_workspace_profiles=profile_ids,
        users={key: users[key].username for key in users},
        created=created_flags,
    )


def result_to_dict(result: PersonasTest2Result) -> dict:
    return {
        "organisation_id": result.organisation_id,
        "organisation_name": C.ORG_NAME,
        "group_primary_id": result.group_primary_id,
        "group_primary_name": C.GROUP_PRIMARY,
        "group_secondary_id": result.group_secondary_id,
        "group_secondary_name": C.GROUP_SECONDARY,
        "learner_a_id": result.learner_a_id,
        "learner_b_id": result.learner_b_id,
        "learner_session_a_id": result.learner_session_a_id,
        "learner_session_b_id": result.learner_session_b_id,
        "trainer_session_id": result.trainer_session_id,
        "trace_id": result.trace_id,
        "tutor_workspace_profiles": result.tutor_workspace_profiles,
        "password": C.DEMO_PASSWORD,
        "users": result.users,
        "created_flags": result.created,
        "urls": {
            "login": "http://localhost:5173/login",
            "app_learner": f"http://localhost:5173/app/session/{result.learner_session_a_id}",
            "app_trainer": "http://localhost:5173/app/trainer/knowledge",
            "app_tutor": "http://localhost:5173/app/tutor",
            "tutor_learner_a": (
                f"http://localhost:5173/app/tutor/group/{result.group_primary_id}"
                f"/learner/{result.learner_a_id}"
            ),
            "admin_profiles": "http://localhost:5173/admin/conversation/learner/profiles",
            "tutor_prompts": "http://localhost:5173/tutor-prompts",
        },
    }


def write_fixture_json(result: PersonasTest2Result, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
