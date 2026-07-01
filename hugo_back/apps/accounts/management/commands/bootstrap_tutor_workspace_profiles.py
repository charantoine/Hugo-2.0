"""Bootstrap des profils espace tuteur P1 (TutorPrompt + ConductProfile + GlobalProfile)."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.accounts.models import Organisation
from apps.hugo.services.tutor_workspace_bootstrap import (
    PROFILE_PRIMARY_POSTURE,
    TUTOR_WORKSPACE_PROFILE_CODES,
    ensure_tutor_workspace_profiles,
)

ORG_NAME = "Smoke Playwright Org"


class Command(BaseCommand):
    help = "Create/update tutor workspace P1 profiles for an organisation (baseline B)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--org-name",
            default=ORG_NAME,
            help=f"Organisation name (default: {ORG_NAME})",
        )

    def handle(self, *args, **options):
        org_name = options["org_name"]
        org, _ = Organisation.objects.get_or_create(name=org_name)
        profiles = ensure_tutor_workspace_profiles(org)

        payload = {
            "organisation_id": str(org.id),
            "profiles": {
                code: {
                    "id": str(profiles[code].id),
                    "primary_posture": PROFILE_PRIMARY_POSTURE[code],
                }
                for code in TUTOR_WORKSPACE_PROFILE_CODES
            },
        }

        workspace = Path(__file__).resolve().parents[4].parent
        out_path = workspace / "docs-workspace" / "tutor_workspace_profiles.generated.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Tutor workspace profiles ready for {org_name}."))
        for code in TUTOR_WORKSPACE_PROFILE_CODES:
            self.stdout.write(f"  {code}={profiles[code].id}")
