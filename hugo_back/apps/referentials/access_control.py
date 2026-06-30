"""Access-control helpers for group learner visibility."""
from apps.accounts.models import Role
from .models import GroupMembership, TutorLearnerLink


ADMIN_ROLES = {Role.ORGADMIN, Role.SUPERADMIN}
TUTOR_ROLES = {Role.TUTOR, Role.TRAINER, Role.COORDO}
TRAINER_KNOWLEDGE_ROLES = {Role.TRAINER, Role.ORGADMIN, Role.SUPERADMIN}


def is_admin_like(user) -> bool:
    return bool(user and getattr(user, "role", None) in ADMIN_ROLES)


def is_superadmin(user) -> bool:
    return bool(user and getattr(user, "role", None) == Role.SUPERADMIN)


def can_manage_tutor_links(user) -> bool:
    """
    Transitional (2026-06): tutor-link mutations are SUPERADMIN-only.
    ORGADMIN will be added later.
    """
    return is_superadmin(user)


def is_tutor_like(user) -> bool:
    return bool(user and getattr(user, "role", None) in TUTOR_ROLES)


def can_manage_trainer_knowledge(user) -> bool:
    return bool(user and getattr(user, "role", None) in TRAINER_KNOWLEDGE_ROLES)


def _group_member_ids(group_id, organisation_id):
    return GroupMembership.objects.filter(
        group_id=group_id,
        organisation_id=organisation_id,
        user__role=Role.LEARNER,
    ).values_list("user_id", flat=True)


def learner_ids_visible_in_group(user, group_id, organisation_id) -> list:
    """
    Resolve learner ids visible to `user` for one group.

    Rules:
    - ORGADMIN/SUPERADMIN: all learners in the group.
    - TUTOR/TRAINER/COORDO: only linked learners, and tutor+learner must both belong to the group.
    - Learner/others: only self, if in the group.
    """
    learner_ids_qs = _group_member_ids(group_id=group_id, organisation_id=organisation_id)
    if is_admin_like(user):
        return list(learner_ids_qs)

    if is_tutor_like(user):
        tutor_in_group = GroupMembership.objects.filter(
            group_id=group_id,
            organisation_id=organisation_id,
            user_id=user.id,
        ).exists()
        if not tutor_in_group:
            return []
        return list(
            TutorLearnerLink.objects.filter(
                organisation_id=organisation_id,
                group_id=group_id,
                tutor_id=user.id,
                learner_id__in=learner_ids_qs,
            ).values_list("learner_id", flat=True)
        )

    is_self_in_group = GroupMembership.objects.filter(
        group_id=group_id,
        organisation_id=organisation_id,
        user_id=user.id,
    ).exists()
    if is_self_in_group:
        return [user.id]
    return []


def can_access_learner_in_group(user, learner_id, group_id, organisation_id) -> bool:
    if not group_id:
        if is_admin_like(user):
            from apps.accounts.models import User
            return User.objects.filter(
                id=learner_id,
                organisation_id=organisation_id,
            ).exists()
        return str(user.id) == str(learner_id)

    visible_ids = learner_ids_visible_in_group(
        user=user,
        group_id=group_id,
        organisation_id=organisation_id,
    )
    return str(learner_id) in {str(item_id) for item_id in visible_ids}


def tutor_linked_groups_for_learner(tutor_id, learner_id, organisation_id) -> list:
    """Group ids where tutor and learner are explicitly linked."""
    return list(
        TutorLearnerLink.objects.filter(
            organisation_id=organisation_id,
            tutor_id=tutor_id,
            learner_id=learner_id,
        ).values_list("group_id", flat=True)
    )
