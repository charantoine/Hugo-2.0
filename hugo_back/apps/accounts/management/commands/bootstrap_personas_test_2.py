"""Bootstrap personas *_test_2 pour baseline B (sqlite_test)."""
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.accounts.seeds import personas_test_2_constants as C
from apps.accounts.seeds.personas_test_2 import (
    result_to_dict,
    run_personas_test_2_seed,
    write_fixture_json,
)


class Command(BaseCommand):
    help = "Create/update orga_test_2 personas (baseline B sqlite_test, idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--write-fixtures",
            action="store_true",
            help="Write docs-workspace/personas-test-2-fixtures.generated.json",
        )

    def handle(self, *args, **options):
        result = run_personas_test_2_seed()
        payload = result_to_dict(result)

        if options["write_fixtures"]:
            workspace = Path(__file__).resolve().parents[4].parent
            out = workspace / "docs-workspace" / "personas-test-2-fixtures.generated.json"
            write_fixture_json(result, out)
            self.stdout.write(self.style.SUCCESS(f"Fixtures → {out}"))

        self.stdout.write(self.style.SUCCESS("Personas test_2 ready (baseline B)."))
        self.stdout.write(f"  organisation: {C.ORG_NAME} ({payload['organisation_id']})")
        self.stdout.write(f"  group primary: {C.GROUP_PRIMARY} ({payload['group_primary_id']})")
        self.stdout.write(f"  group secondary: {C.GROUP_SECONDARY} ({payload['group_secondary_id']})")
        self.stdout.write(f"  password: {C.DEMO_PASSWORD}")
        for role, username in payload["users"].items():
            flag = "created" if result.created.get(f"user_{role}") else "reused"
            self.stdout.write(f"  {role}: {username} ({flag})")
        self.stdout.write(f"  learner_session_a: {payload['learner_session_a_id']}")
        self.stdout.write(f"  trainer_session: {payload['trainer_session_id']}")
        self.stdout.write(f"  trace: {payload['trace_id']}")
        self.stdout.write(f"  tutor_workspace_profiles: {len(payload['tutor_workspace_profiles'])} profils")
