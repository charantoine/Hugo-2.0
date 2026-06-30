"""Canonical group / tutor-learner attachments for seeds (mirrors API rules)."""
from __future__ import annotations

from apps.accounts.models import Role
from apps.referentials.models import GroupMembership, TutorLearnerLink


def ensure_group_membership(organisation, group, user) -> GroupMembership:
    """
    Ensure user is a member of group.

    DB unique key is (group, user) — organisation_id must be kept in sync via defaults.
    """
    membership, _ = GroupMembership.objects.update_or_create(
        group=group,
        user=user,
        defaults={"organisation_id": organisation.id},
    )
    return membership


def ensure_tutor_learner_link(organisation, group, tutor, learner) -> TutorLearnerLink:
    """Tutor and learner must both be group members before linking (API rule)."""
    if tutor.role not in {Role.TUTOR, Role.TRAINER, Role.COORDO}:
        raise ValueError(f"Expected tutor-like role, got {tutor.role}")
    if learner.role != Role.LEARNER:
        raise ValueError(f"Expected learner role, got {learner.role}")
    ensure_group_membership(organisation, group, tutor)
    ensure_group_membership(organisation, group, learner)
    link, _ = TutorLearnerLink.objects.get_or_create(
        organisation_id=organisation.id,
        group=group,
        tutor=tutor,
        learner=learner,
    )
    return link


def ensure_group_staff_memberships(organisation, group, users) -> list[GroupMembership]:
    return [ensure_group_membership(organisation, group, user) for user in users]
