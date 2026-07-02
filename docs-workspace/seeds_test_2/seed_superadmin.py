# Source extraite de: scripts/check_demo_superadmin.py, apps/accounts/models.py
# Date: 2026-07-02
# Auteur: CTO kit
#
# Usage:
#   python manage.py shell < ../docs-workspace/seeds_test_2/seed_superadmin.py

import os

from apps.accounts.models import Organisation, Role, User


SEED_PASSWORD = os.environ.get("SEED_PASSWORD", "hugo_test_2!")
SUPERADMIN = {
    "organisation_name": "Demo Hugo Org",
    "username": "demo.superadmin",
    "email": "demo.superadmin@demo.local",
    "role": Role.SUPERADMIN,
    "is_superuser": True,
    "is_staff": True,
    "is_active": True,
}


def run() -> None:
    org, _ = Organisation.objects.get_or_create(name=SUPERADMIN["organisation_name"])
    user, created = User.objects.get_or_create(
        username=SUPERADMIN["username"],
        defaults={
            "organisation": org,
            "email": SUPERADMIN["email"],
            "role": SUPERADMIN["role"],
            "is_superuser": SUPERADMIN["is_superuser"],
            "is_staff": SUPERADMIN["is_staff"],
            "is_active": SUPERADMIN["is_active"],
        },
    )

    user.organisation = org
    user.email = SUPERADMIN["email"]
    user.role = SUPERADMIN["role"]
    user.is_superuser = SUPERADMIN["is_superuser"]
    user.is_staff = SUPERADMIN["is_staff"]
    user.is_active = SUPERADMIN["is_active"]
    user.set_password(SEED_PASSWORD)
    user.save()

    print(
        f"[seed_superadmin] email={user.email or '(empty)'} "
        f"username={user.username} created={created}"
    )


run()
