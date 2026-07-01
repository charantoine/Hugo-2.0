"""Fixture de référence baseline B — reconfiguration chats tuteur/formateur (P1)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.accounts.models import Organisation, Role, User
from apps.hugo.models import HugoMessage, HugoSession, Trace, TutorPrompt
from apps.hugo.services.tutor_workspace_bootstrap import ensure_tutor_workspace_profiles
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


VERBATIM_PRIVATE_MARKER = "MORNING_RECONF_PRIVATE_VERBATIM_7c4e"
VERBATIM_SHARED_MARKER = "MORNING_RECONF_SHARED_VERBATIM_8d5f"


@dataclass
class MorningReconfBaselineB:
    organisation: Organisation
    group: Group
    superadmin: User
    orgadmin: User
    trainer: User
    tutor: User
    learner: User
    coordo: User
    tutor_workspace_profiles: dict
    learner_session: HugoSession
    learner_session_private: HugoSession
    trainer_session: HugoSession
    linked_trace: Trace
    password: str = "morning-reconf-pass"


def build_morning_reconf_baseline_b(
    *,
    org_name: str = "Morning Reconf Baseline B Org",
    group_name: str = "Morning Reconf Group",
) -> MorningReconfBaselineB:
    org, _ = Organisation.objects.get_or_create(name=org_name)
    group, _ = Group.objects.get_or_create(organisation=org, name=group_name)

    users: dict[str, User] = {}
    for username, role in {
        "morning_superadmin": Role.SUPERADMIN,
        "morning_orgadmin": Role.ORGADMIN,
        "morning_trainer": Role.TRAINER,
        "morning_tutor": Role.TUTOR,
        "morning_learner": Role.LEARNER,
        "morning_coordo": Role.COORDO,
    }.items():
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "organisation": org,
                "role": role,
            },
        )
        if created or user.organisation_id != org.id:
            user.organisation = org
            user.role = role
            user.set_password("morning-reconf-pass")
            user.save()
        users[username.split("_", 1)[1]] = user

    for user in users.values():
        GroupMembership.objects.get_or_create(
            organisation=org,
            group=group,
            user=user,
        )

    TutorLearnerLink.objects.get_or_create(
        organisation=org,
        group=group,
        tutor=users["tutor"],
        learner=users["learner"],
    )

    tutor_profiles = ensure_tutor_workspace_profiles(org)

    learner_default_prompt = TutorPrompt.objects.filter(
        organisation=org,
        is_default=True,
    ).first()
    if learner_default_prompt is None:
        learner_default_prompt = TutorPrompt.objects.create(
            organisation=org,
            code="morning_learner_default",
            name="Learner default prompt",
            system_template="Tu accompagnes l'apprenant {conversation_profile}",
            user_template="{situation_content}",
            is_default=True,
            is_active=True,
        )

    learner_session = HugoSession.objects.create(
        organisation=org,
        group=group,
        learner=users["learner"],
        share_verbatim=False,
        share_summary=False,
        share_evidence=False,
    )
    learner_session_private = HugoSession.objects.create(
        organisation=org,
        group=group,
        learner=users["learner"],
        share_verbatim=False,
    )
    HugoMessage.objects.create(
        organisation=org,
        session=learner_session_private,
        role=HugoMessage.Role.LEARNER,
        content=VERBATIM_PRIVATE_MARKER,
    )

    shared_session = HugoSession.objects.create(
        organisation=org,
        group=group,
        learner=users["learner"],
        share_verbatim=True,
    )
    HugoMessage.objects.create(
        organisation=org,
        session=shared_session,
        role=HugoMessage.Role.LEARNER,
        content=VERBATIM_SHARED_MARKER,
    )

    trainer_session = HugoSession.objects.create(
        organisation=org,
        group=group,
        learner=users["trainer"],
    )

    linked_trace = Trace.objects.create(
        organisation=org,
        session=learner_session,
        payload_structured={},
    )

    return MorningReconfBaselineB(
        organisation=org,
        group=group,
        superadmin=users["superadmin"],
        orgadmin=users["orgadmin"],
        trainer=users["trainer"],
        tutor=users["tutor"],
        learner=users["learner"],
        coordo=users["coordo"],
        tutor_workspace_profiles=tutor_profiles,
        learner_session=learner_session,
        learner_session_private=learner_session_private,
        trainer_session=trainer_session,
        linked_trace=linked_trace,
    )


def as_fixture_dict(world: MorningReconfBaselineB) -> dict[str, Any]:
    return {
        "organisation_id": str(world.organisation.id),
        "group_id": str(world.group.id),
        "learner_id": str(world.learner.id),
        "tutor_id": str(world.tutor.id),
        "trainer_id": str(world.trainer.id),
        "learner_session_id": str(world.learner_session.id),
        "trainer_session_id": str(world.trainer_session.id),
        "tutor_workspace_profiles": {
            code: str(profile.id) for code, profile in world.tutor_workspace_profiles.items()
        },
    }
