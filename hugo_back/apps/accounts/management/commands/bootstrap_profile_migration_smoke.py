"""Bootstrap fixtures for learner profile migration smoke tests (4 scenarios)."""
import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Organisation, Role
from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import HugoSession, LearnerConversationGlobalProfile, TutorPrompt
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink

SMOKE_PASSWORD = "smoke-pass-2026"
ORG_NAME = "Smoke Playwright Org"


class Command(BaseCommand):
    help = "Create profile-migration smoke groups/sessions for Playwright (cases 1–4)."

    def _ensure_prompt(self, org, code, posture):
        prompt, _ = TutorPrompt.objects.get_or_create(
            organisation=org,
            code=code,
            defaults={
                "name": code,
                "system_template": f"sys {code}",
                "user_template": f"usr {code}",
                "conversation_profile": posture,
                "is_active": True,
            },
        )
        return prompt

    def _ensure_profile(self, org, name, **slots):
        profile, _ = LearnerConversationGlobalProfile.objects.update_or_create(
            organisation=org,
            name=name,
            defaults={
                "status": LearnerConversationGlobalProfile.Status.ACTIVE,
                **slots,
            },
        )
        return profile

    def handle(self, *args, **options):
        User = get_user_model()
        org, _ = Organisation.objects.get_or_create(name=ORG_NAME)
        learner = User.objects.get(username="smoke_learner")

        refl = self._ensure_prompt(org, "smoke-refl", ConversationPosture.REFLECTIVE_AFEST.value)
        diag = self._ensure_prompt(org, "smoke-diag", ConversationPosture.DIAGNOSTIC.value)

        profile_a = self._ensure_profile(
            org,
            "Smoke Profil Unique",
            is_default=False,
            reflective_tutor_prompt=refl,
            diagnostic_tutor_prompt=diag,
        )
        profile_b1 = self._ensure_profile(
            org,
            "Smoke Profil Alpha",
            is_default=False,
            reflective_tutor_prompt=refl,
        )
        profile_b2 = self._ensure_profile(
            org,
            "Smoke Profil Beta",
            is_default=False,
            diagnostic_tutor_prompt=diag,
        )

        legacy_prompt = self._ensure_prompt(org, "smoke-legacy-session", ConversationPosture.REFLECTIVE_AFEST.value)

        groups_spec = {
            "one": ("ProfileSmoke-One", profile_a),
            "multi": ("ProfileSmoke-Multi", None),
            "none": ("ProfileSmoke-None", None),
        }
        fixtures_groups = {}
        for key, (name, default_profile) in groups_spec.items():
            group, _ = Group.objects.get_or_create(organisation=org, name=name)
            group.default_learner_conversation_profile = default_profile
            group.default_tutor_prompt = None
            group.save(update_fields=["default_learner_conversation_profile", "default_tutor_prompt"])
            GroupMembership.objects.get_or_create(organisation=org, group=group, user=learner)
            fixtures_groups[key] = {
                "group_id": str(group.id),
                "default_profile_id": str(default_profile.id) if default_profile else None,
            }

        none_group = Group.objects.get(organisation=org, name="ProfileSmoke-None")
        legacy_session = (
            HugoSession.objects.filter(
                organisation=org,
                learner=learner,
                group=none_group,
            )
            .order_by("created_at")
            .first()
        )
        if legacy_session is None:
            legacy_session = HugoSession.objects.create(
                organisation=org,
                learner=learner,
                group=none_group,
            )
        legacy_session.tutor_prompt = legacy_prompt
        legacy_session.learner_conversation_profile = None
        legacy_session.save(update_fields=["tutor_prompt", "learner_conversation_profile"])

        out = {
            "password": SMOKE_PASSWORD,
            "learner": "smoke_learner",
            "profiles": {
                "single": str(profile_a.id),
                "alpha": str(profile_b1.id),
                "beta": str(profile_b2.id),
            },
            "groups": fixtures_groups,
            "legacy_session_id": str(legacy_session.id),
        }

        workspace = Path(__file__).resolve().parents[5]
        targets = [
            workspace / "hugo-hugolucia/frontend_1.8/tests_playwright/profile-smoke-fixtures.json",
            workspace / "hugo-hugolucia/frontend_1.8/tests_playwright/smoke-fixtures.json",
        ]
        for path in targets:
            if path.name == "smoke-fixtures.json" and path.exists():
                base = json.loads(path.read_text(encoding="utf-8"))
                base["profile_migration"] = out
                path.write_text(json.dumps(base, indent=2), encoding="utf-8")
            elif path.name == "profile-smoke-fixtures.json":
                path.write_text(json.dumps(out, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS("Profile migration smoke fixtures ready."))
        self.stdout.write(json.dumps(out, indent=2))
