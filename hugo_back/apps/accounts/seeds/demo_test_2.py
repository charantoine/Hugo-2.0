"""Orchestrate the OF_test_2 / bac_pro__test_2 demo seed scenario."""
from __future__ import annotations

import json
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.accounts.models import Organisation, Role
from apps.accounts.seeds.clone_conversation_profile import clone_global_profile, resolve_source_profile
from apps.accounts.seeds import demo_test_2_constants as C
from apps.accounts.seeds.group_attachments import (
    ensure_group_membership,
    ensure_tutor_learner_link,
)
from apps.accounts.seeds.referential_rncp38878 import ensure_rncp38878_for_org
from apps.referentials.models import Group, ReferentialConfig


@dataclass
class SeedResult:
    organisation_id: str
    group_id: str
    referential_id: str | None
    profile_id: str | None
    profile_source: str
    users: dict[str, str]


def _ensure_user(org, username: str, role: str):
    User = get_user_model()
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
    return user


@transaction.atomic
def run_demo_test_2_seed(
    *,
    source_org_name: str = C.DEFAULT_SOURCE_ORG_NAME,
    source_profile_name: str = C.DEFAULT_SOURCE_PROFILE_NAME,
    source_group_name: str = C.DEFAULT_SOURCE_GROUP_NAME,
    source_learner_username: str = C.DEFAULT_SOURCE_LEARNER_USERNAME,
    force_reimport_referential: bool = False,
) -> SeedResult:
    org, _ = Organisation.objects.get_or_create(name=C.ORG_NAME)

    users = {
        "learner": _ensure_user(org, C.LEARNER_USERNAME, Role.LEARNER),
        "tutor": _ensure_user(org, C.TUTOR_USERNAME, Role.TUTOR),
        "trainer": _ensure_user(org, C.TRAINER_USERNAME, Role.TRAINER),
    }

    group, _ = Group.objects.get_or_create(organisation=org, name=C.GROUP_NAME)

    for user in users.values():
        ensure_group_membership(org, group, user)

    ensure_tutor_learner_link(org, group, users["tutor"], users["learner"])

    referential = ensure_rncp38878_for_org(
        org.id,
        force_reimport=force_reimport_referential,
    )
    ReferentialConfig.objects.update_or_create(
        group=group,
        defaults={
            "organisation_id": org.id,
            "referential": referential,
        },
    )

    profile_id = None
    profile_source = "skipped_no_source_org"
    source_org = Organisation.objects.filter(name=source_org_name).first()
    if source_org:
        source_profile, profile_source = resolve_source_profile(
            source_org,
            profile_name=source_profile_name,
            source_group_name=source_group_name,
            source_learner_username=source_learner_username,
        )
        if source_profile:
            cloned = clone_global_profile(
                source_profile,
                org.id,
                target_name=C.TARGET_PROFILE_NAME,
                target_group_id=group.id,
            )
            profile_id = str(cloned.id)
            group.default_learner_conversation_profile = cloned
            group.default_tutor_prompt = None
            group.save(update_fields=["default_learner_conversation_profile", "default_tutor_prompt"])
        else:
            profile_source = f"not_found:{profile_source}"

    return SeedResult(
        organisation_id=str(org.id),
        group_id=str(group.id),
        referential_id=str(referential.id) if referential else None,
        profile_id=profile_id,
        profile_source=profile_source,
        users={key: user.username for key, user in users.items()},
    )


def seed_result_to_dict(result: SeedResult) -> dict:
    return {
        "organisation_id": result.organisation_id,
        "organisation_name": C.ORG_NAME,
        "group_id": result.group_id,
        "group_name": C.GROUP_NAME,
        "referential_source_ref": C.REFERENTIAL_SOURCE_REF,
        "referential_id": result.referential_id,
        "learner_conversation_profile_id": result.profile_id,
        "profile_clone_source": result.profile_source,
        "password": C.DEMO_PASSWORD,
        "users": result.users,
    }


def write_fixture_json(result: SeedResult, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seed_result_to_dict(result), indent=2), encoding="utf-8")
