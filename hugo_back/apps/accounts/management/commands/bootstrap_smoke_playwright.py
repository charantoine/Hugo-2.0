"""Bootstrap deterministic fixtures for Playwright smoke tests (cluster 8 / cluster 16)."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoMessage, HugoSession, Trace, TrainerKnowledgeItem
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


SMOKE_PASSWORD = "smoke-pass-2026"
ORG_NAME = "Smoke Playwright Org"
GROUP_NAME = "Smoke Group"
VERBATIM_MARKER = "VERBATIM_SECRET_SMOKE_DO_NOT_SHOW"

CLUSTER16_GROUPS = {
    "youth": ("Smoke C16 Youth", "youth"),
    "adult": ("Smoke C16 Adult", "adult"),
    "professional": ("Smoke C16 Professional", "professional"),
}


class Command(BaseCommand):
    help = "Create/update smoke users and data for Playwright tests (cluster 8 / 16)."

    def _ensure_cluster16_session(self, org, learner, group_name: str, display_profile: str):
        group, _ = Group.objects.get_or_create(
            organisation=org,
            name=group_name,
            defaults={"learner_display_profile": display_profile},
        )
        if group.learner_display_profile != display_profile:
            group.learner_display_profile = display_profile
            group.save(update_fields=["learner_display_profile"])

        GroupMembership.objects.get_or_create(
            organisation=org,
            group=group,
            user=learner,
        )

        progress = {
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [
                {
                    "branch_id": f"branch-{display_profile}",
                    "theme_label": f"Thème démo {display_profile}",
                    "objective_label": "Objectif actif démo",
                    "exploration_level": "orange",
                    "is_active": True,
                    "reason_codes": [],
                }
            ],
            "active_branches_count": 1,
            "priority_branch_id": f"branch-{display_profile}",
            "dispersion_risk": display_profile == "youth",
            "overall_maturity": "orange",
            "synthesis_eligible": True,
            "evaluation_eligible": False,
            "missing_for_next_level": ["Nommer une action concrète déjà réalisée."],
            "reason_codes": ["evaluation_blocked_maturity"],
        }
        session, created = HugoSession.objects.get_or_create(
            organisation=org,
            learner=learner,
            group=group,
            defaults={
                "share_verbatim": False,
                "share_summary": True,
                "posture": "reflective_afest",
                "conversation_progress": progress,
            },
        )
        if not created:
            session.conversation_progress = progress
            session.posture = "reflective_afest"
            session.save(update_fields=["conversation_progress", "posture"])

        progress["session_id"] = str(session.id)
        session.conversation_progress = progress
        session.save(update_fields=["conversation_progress"])

        HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).delete()
        HugoMessage.objects.create(
            organisation=org,
            session=session,
            role=HugoMessage.Role.LEARNER,
            content=VERBATIM_MARKER,
            llm_request_payload={
                "turn_state": {
                    "covered_points": [f"fait_confirme_{display_profile}"],
                    "remaining_open_points": [f"point_ouvert_{display_profile}"],
                }
            },
        )
        return session

    def handle(self, *args, **options):
        User = get_user_model()
        org, _ = Organisation.objects.get_or_create(name=ORG_NAME)
        group, _ = Group.objects.get_or_create(organisation=org, name=GROUP_NAME)

        users_spec = {
            "smoke_superadmin": Role.SUPERADMIN,
            "smoke_tutor": Role.TUTOR,
            "smoke_trainer": Role.TRAINER,
            "smoke_orgadmin": Role.ORGADMIN,
            "smoke_learner": Role.LEARNER,
            "smoke_coordo": Role.COORDO,
        }
        users = {}
        for username, role in users_spec.items():
            extra = {
                "organisation": org,
                "role": role,
                "is_staff": role in {Role.ORGADMIN, Role.SUPERADMIN},
            }
            if role == Role.SUPERADMIN:
                extra["is_superuser"] = True
            user, created = User.objects.get_or_create(
                username=username,
                defaults=extra,
            )
            if not created:
                user.organisation = org
                user.role = role
                user.is_staff = role in {Role.ORGADMIN, Role.SUPERADMIN}
                if role == Role.SUPERADMIN:
                    user.is_superuser = True
            user.set_password(SMOKE_PASSWORD)
            user.save()
            users[username] = user
            GroupMembership.objects.get_or_create(
                organisation=org,
                group=group,
                user=user,
            )

        TutorLearnerLink.objects.get_or_create(
            organisation=org,
            group=group,
            tutor=users["smoke_tutor"],
            learner=users["smoke_learner"],
        )

        session, _ = HugoSession.objects.get_or_create(
            organisation=org,
            learner=users["smoke_learner"],
            group=group,
            defaults={
                "share_verbatim": False,
                "share_summary": True,
                "conversation_progress": {
                    "session_id": "pending",
                    "posture": "reflective_afest",
                    "active_branches_count": 0,
                    "overall_maturity": "orange",
                    "synthesis_eligible": False,
                    "evaluation_eligible": False,
                    "reason_codes": [],
                },
            },
        )
        if session.conversation_progress.get("session_id") == "pending":
            session.conversation_progress["session_id"] = str(session.id)
            session.save(update_fields=["conversation_progress"])

        HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).delete()
        HugoMessage.objects.create(
            organisation=org,
            session=session,
            role=HugoMessage.Role.LEARNER,
            content=VERBATIM_MARKER,
        )

        trace, _ = Trace.objects.get_or_create(
            organisation=org,
            session=session,
            defaults={"payload_structured": {"session_id": str(session.id)}},
        )

        item, _ = TrainerKnowledgeItem.objects.get_or_create(
            organisation=org,
            content="Smoke knowledge item for Playwright",
            defaults={"status": "declared", "content_type": "mastery_criterion"},
        )

        cluster16_sessions = {}
        for key, (group_name, profile) in CLUSTER16_GROUPS.items():
            c16_session = self._ensure_cluster16_session(
                org, users["smoke_learner"], group_name, profile
            )
            cluster16_sessions[key] = str(c16_session.id)

        fixtures = {
            "organisation_id": str(org.id),
            "organisation_name": org.name,
            "group_name": GROUP_NAME,
            "group_id": str(group.id),
            "learner_id": str(users["smoke_learner"].id),
            "session_id": str(session.id),
            "trace_id": str(trace.id),
            "knowledge_item_id": str(item.id),
            "password": SMOKE_PASSWORD,
            "users": {name: name for name in users_spec},
            "verbatim_marker": VERBATIM_MARKER,
            "cluster16_sessions": cluster16_sessions,
        }

        import json
        from pathlib import Path

        workspace = Path(__file__).resolve().parents[4].parent
        out_paths = [
            workspace / "hugo-hugolucia" / "frontend_1.8" / "tests_playwright" / "smoke-fixtures.json",
            workspace / "docs-workspace" / "smoke-fixtures.generated.json",
        ]
        for path in out_paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(fixtures, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS("Smoke fixtures ready."))
        for username in users_spec:
            self.stdout.write(f"  {username} / {SMOKE_PASSWORD}")
        self.stdout.write(f"  group_id={fixtures['group_id']}")
        self.stdout.write(f"  learner_id={fixtures['learner_id']}")
        for profile, sid in cluster16_sessions.items():
            self.stdout.write(f"  cluster16_{profile}={sid}")
