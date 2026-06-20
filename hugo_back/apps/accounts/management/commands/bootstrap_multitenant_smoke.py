"""Bootstrap two-org fixtures for multi-tenant Playwright smoke (SMOKE_RUN_TENANT=1)."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoSession
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


PASSWORD = "tenant-smoke-2026"
ORG_A = "Tenant Smoke Org A"
ORG_B = "Tenant Smoke Org B"


class Command(BaseCommand):
    help = "Create two organisations + personas for multi-tenant smoke tests."

    def handle(self, *args, **options):
        User = get_user_model()
        org_a, _ = Organisation.objects.get_or_create(name=ORG_A)
        org_b, _ = Organisation.objects.get_or_create(name=ORG_B)

        def user(org, username, role, **extra):
            u, created = User.objects.get_or_create(
                username=username,
                defaults={"organisation": org, "role": role, **extra},
            )
            if not created:
                u.organisation = org
                u.role = role
            u.set_password(PASSWORD)
            u.save()
            return u

        superadmin = user(
            org_a,
            "tenant_superadmin",
            Role.SUPERADMIN,
            is_superuser=True,
            is_staff=True,
        )
        orgadmin_a = user(org_a, "tenant_orgadmin_a", Role.ORGADMIN, is_staff=True)
        orgadmin_b = user(org_b, "tenant_orgadmin_b", Role.ORGADMIN, is_staff=True)
        tutor_a = user(org_a, "tenant_tutor_a", Role.TUTOR)
        learner_a = user(org_a, "tenant_learner_a", Role.LEARNER)
        learner_b = user(org_b, "tenant_learner_b", Role.LEARNER)

        group_a, _ = Group.objects.get_or_create(organisation=org_a, name="Tenant Group A")
        group_b, _ = Group.objects.get_or_create(organisation=org_b, name="Tenant Group B")

        for g, org, members in (
            (group_a, org_a, (tutor_a, learner_a, orgadmin_a)),
            (group_b, org_b, (learner_b, orgadmin_b)),
        ):
            for member in members:
                GroupMembership.objects.get_or_create(
                    organisation=org,
                    group=g,
                    user=member,
                )

        TutorLearnerLink.objects.get_or_create(
            organisation=org_a,
            group=group_a,
            tutor=tutor_a,
            learner=learner_a,
        )

        session_a, _ = HugoSession.objects.get_or_create(
            organisation=org_a,
            learner=learner_a,
            group=group_a,
        )
        session_b, _ = HugoSession.objects.get_or_create(
            organisation=org_b,
            learner=learner_b,
            group=group_b,
        )

        fixtures = {
            "password": PASSWORD,
            "org_a": {"id": str(org_a.id), "name": org_a.name},
            "org_b": {"id": str(org_b.id), "name": org_b.name},
            "group_a_id": str(group_a.id),
            "group_b_id": str(group_b.id),
            "session_a_id": str(session_a.id),
            "session_b_id": str(session_b.id),
            "users": {
                "superadmin": superadmin.username,
                "orgadmin_a": orgadmin_a.username,
                "orgadmin_b": orgadmin_b.username,
                "tutor_a": tutor_a.username,
                "learner_a": learner_a.username,
                "learner_b": learner_b.username,
            },
        }

        workspace = Path(__file__).resolve().parents[4].parent
        out = workspace / "hugo-hugolucia" / "frontend_1.8" / "tests_playwright" / "tenant-smoke-fixtures.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(fixtures, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Tenant smoke fixtures → {out}"))
        self.stdout.write(f"  password={PASSWORD}")
        for key, username in fixtures["users"].items():
            self.stdout.write(f"  {key}: {username}")
