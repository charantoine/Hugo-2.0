"""Bootstrap OF_test_2 demo accounts (idempotent).

Creates or updates:
  - organisation OF_test_2
  - group bac_pro__test_2
  - apprenant_test_2 / tuteur_test_2 / formateur_test_2 (password demo123)
  - RNCP38878 referential linked to the group
  - learner conversation profile cloned from Demo Hugo Org mk1 fixtures

Re-run safe: users/passwords/memberships/links are upserted; referential is reused
unless --force-reimport-referential; profile and prompts are update_or_create by stable keys.
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.seeds import demo_test_2_constants as C
from apps.accounts.seeds.demo_test_2 import run_demo_test_2_seed, seed_result_to_dict, write_fixture_json


class Command(BaseCommand):
    help = "Create/update OF_test_2 demo org, users, group, RNCP38878 and mk1 conversation profile."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-org",
            default=C.DEFAULT_SOURCE_ORG_NAME,
            help=f"Organisation to clone conversation config from (default: {C.DEFAULT_SOURCE_ORG_NAME}).",
        )
        parser.add_argument(
            "--source-profile",
            default=C.DEFAULT_SOURCE_PROFILE_NAME,
            help=f"LearnerConversationGlobalProfile name in source org (default: {C.DEFAULT_SOURCE_PROFILE_NAME}).",
        )
        parser.add_argument(
            "--source-group",
            default=C.DEFAULT_SOURCE_GROUP_NAME,
            help=f"Fallback group name in source org (default: {C.DEFAULT_SOURCE_GROUP_NAME}).",
        )
        parser.add_argument(
            "--source-learner",
            default=C.DEFAULT_SOURCE_LEARNER_USERNAME,
            help=(
                "Fallback learner username for session profile "
                f"(default: {C.DEFAULT_SOURCE_LEARNER_USERNAME}; alias historique apprenant_test_1 non documenté en base)."
            ),
        )
        parser.add_argument(
            "--force-reimport-referential",
            action="store_true",
            help="Import a fresh RNCP38878 even if one already exists in OF_test_2.",
        )
        parser.add_argument(
            "--write-fixtures",
            action="store_true",
            help="Write docs-workspace/demo-test-2-fixtures.generated.json",
        )

    def handle(self, *args, **options):
        try:
            result = run_demo_test_2_seed(
                source_org_name=options["source_org"].strip(),
                source_profile_name=options["source_profile"].strip(),
                source_group_name=options["source_group"].strip(),
                source_learner_username=options["source_learner"].strip(),
                force_reimport_referential=options["force_reimport_referential"],
            )
        except FileNotFoundError as err:
            raise CommandError(str(err)) from err

        payload = seed_result_to_dict(result)
        if options["write_fixtures"]:
            workspace = Path(__file__).resolve().parents[4].parent
            out = workspace / "docs-workspace" / "demo-test-2-fixtures.generated.json"
            write_fixture_json(result, out)
            self.stdout.write(self.style.SUCCESS(f"Fixtures written → {out}"))

        self.stdout.write(self.style.SUCCESS("Demo test_2 seed ready (idempotent)."))
        self.stdout.write(f"  organisation: {payload['organisation_name']} ({payload['organisation_id']})")
        self.stdout.write(f"  group: {payload['group_name']} ({payload['group_id']})")
        self.stdout.write(f"  referential: {payload['referential_source_ref']} ({payload['referential_id']})")
        self.stdout.write(f"  profile: {C.TARGET_PROFILE_NAME} ({payload['learner_conversation_profile_id']})")
        self.stdout.write(f"  profile_clone_source: {payload['profile_clone_source']}")
        self.stdout.write(f"  password: {payload['password']}")
        for role, username in payload["users"].items():
            self.stdout.write(f"  {role}: {username}")

        if not payload["learner_conversation_profile_id"]:
            self.stdout.write(
                self.style.WARNING(
                    "Conversation profile not cloned — source org/profile missing. "
                    f"Ensure {options['source_org']} exists with {options['source_profile']} "
                    f"or group {options['source_group']} / learner {options['source_learner']}."
                )
            )
