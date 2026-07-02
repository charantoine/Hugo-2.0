# Source extraite de: apps/accounts/seeds/demo_test_2.py, personas_test_2.py
# Date: 2026-07-02
# Auteur: CTO kit
#
# Usage:
#   python manage.py shell < ../docs-workspace/seeds_test_2/seed_accounts_test_2.py

import os

from apps.accounts.models import Organisation, Role, User
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


SEED_PASSWORD = os.environ.get("SEED_PASSWORD", "hugo_test_2!")

SEED_DATA = [
    {
        "organisation": "OF_test_2",
        "groups": ["bac_pro__test_2"],
        "users": [
            {"username": "apprenant_test_2", "role": Role.LEARNER, "email": ""},
            {"username": "tuteur_test_2", "role": Role.TUTOR, "email": ""},
            {"username": "formateur_test_2", "role": Role.TRAINER, "email": ""},
        ],
        "links": [("tuteur_test_2", "apprenant_test_2", "bac_pro__test_2")],
    },
    {
        "organisation": "orga_test_2",
        "groups": ["groupe_test_2_principal", "groupe_test_2_secondaire"],
        "users": [
            {
                "username": "superadmin_test_2",
                "role": Role.SUPERADMIN,
                "is_superuser": True,
                "is_staff": True,
                "email": "",
            },
            {"username": "orgadmin_test_2", "role": Role.ORGADMIN, "is_staff": True, "email": ""},
            {"username": "coordo_test_2", "role": Role.COORDO, "email": ""},
            {"username": "trainer_test_2", "role": Role.TRAINER, "email": ""},
            {"username": "tutor_test_2", "role": Role.TUTOR, "email": ""},
            {"username": "learner_test_2_a", "role": Role.LEARNER, "email": ""},
            {"username": "learner_test_2_b", "role": Role.LEARNER, "email": ""},
        ],
        "links": [("tutor_test_2", "learner_test_2_a", "groupe_test_2_principal")],
    },
]


def _ensure_user(org: Organisation, user_spec: dict) -> tuple[User, bool]:
    user, created = User.objects.get_or_create(
        username=user_spec["username"],
        defaults={
            "organisation": org,
            "role": user_spec["role"],
            "email": user_spec.get("email", ""),
            "is_staff": user_spec.get("is_staff", False),
            "is_superuser": user_spec.get("is_superuser", False),
            "is_active": True,
        },
    )
    user.organisation = org
    user.role = user_spec["role"]
    user.email = user_spec.get("email", "")
    user.is_staff = user_spec.get("is_staff", False)
    user.is_superuser = user_spec.get("is_superuser", False)
    user.is_active = True
    user.set_password(SEED_PASSWORD)
    user.save()
    return user, created


def run() -> None:
    summary = []
    for org_spec in SEED_DATA:
        org, org_created = Organisation.objects.get_or_create(name=org_spec["organisation"])
        groups = {}
        for group_name in org_spec["groups"]:
            group, group_created = Group.objects.get_or_create(organisation=org, name=group_name)
            groups[group_name] = group
            summary.append(
                f"[group] org={org.name} group={group_name} created={group_created}"
            )

        users = {}
        for user_spec in org_spec["users"]:
            user, created = _ensure_user(org, user_spec)
            users[user.username] = user
            summary.append(
                f"[user] org={org.name} username={user.username} role={user.role} created={created}"
            )

        for username, user in users.items():
            target_groups = list(groups.keys())
            if org.name == "orga_test_2" and username == "learner_test_2_b":
                target_groups = ["groupe_test_2_principal", "groupe_test_2_secondaire"]
            for group_name in target_groups:
                _, membership_created = GroupMembership.objects.get_or_create(
                    organisation=org,
                    group=groups[group_name],
                    user=user,
                )
                summary.append(
                    f"[membership] org={org.name} group={group_name} user={username} created={membership_created}"
                )

        for tutor_username, learner_username, group_name in org_spec["links"]:
            _, link_created = TutorLearnerLink.objects.get_or_create(
                organisation=org,
                group=groups[group_name],
                tutor=users[tutor_username],
                learner=users[learner_username],
            )
            summary.append(
                f"[link] org={org.name} group={group_name} tutor={tutor_username} "
                f"learner={learner_username} created={link_created}"
            )

        summary.append(f"[organisation] name={org.name} created={org_created}")

    print("[seed_accounts_test_2] resume")
    for line in summary:
        print(f"  - {line}")


run()
