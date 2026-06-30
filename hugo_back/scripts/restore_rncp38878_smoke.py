#!/usr/bin/env python3
"""Import RNCP38878 (enriched) into Smoke Playwright Org and link smoke groups.

OBSOLÈTE (juin 2026) — IDs hardcodés, hors commande manage.py.
Préférer : `python manage.py bootstrap_demo_test_2` ou `referential_rncp38878.py`
via les seeds documentés dans `docs-workspace/seed-strategies.md`.

Usage (from hugo_back/, with config.settings.dev and hugo_poc running):
  python scripts/restore_rncp38878_smoke.py

Requires smoke_orgadmin in Smoke Playwright Org.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT.parent / "docs-workspace" / "RNCP38878.json"

SMOKE_GROUP_IDS = [
    "0ff5014c-ff9b-4363-b613-e03bbdc033b8",  # Smoke Group
    "06b0a952-376f-4c18-b922-4640ccc64755",  # Smoke C16 Youth
    "2424d35e-2055-43b5-a7ab-1663c02a1ea2",  # Smoke C16 Adult
    "61092635-0ccf-4b31-a383-075042aac9d4",  # Smoke C16 Professional
]


def main() -> int:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    sys.path.insert(0, str(ROOT))
    import django

    django.setup()

    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    if not JSON_PATH.is_file():
        print(f"Missing JSON: {JSON_PATH}", file=sys.stderr)
        return 1

    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    user = get_user_model().objects.get(username="smoke_orgadmin")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post("/referentials/import-v2/", payload, format="json")
    if resp.status_code != 201:
        print("Import failed:", resp.status_code, resp.data, file=sys.stderr)
        return 1

    ref_id = resp.data["id"]
    print("Imported referential:", ref_id, resp.data)

    for gid in SMOKE_GROUP_IDS:
        link = client.put(
            f"/groups/{gid}/referential-config/",
            {"referential_id": ref_id},
            format="json",
        )
        if link.status_code not in (200, 201):
            print(f"Link failed for group {gid}:", link.status_code, link.data, file=sys.stderr)
            return 1
        print("Linked group", gid)

    print("Done. smoke_learner groups now point to referential", ref_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
