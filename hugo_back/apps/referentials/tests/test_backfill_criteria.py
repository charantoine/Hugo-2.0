import importlib

from django.test import TestCase

from apps.accounts.models import Organisation
from apps.referentials.models import Referential, ReferentialItem, ReferentialCriterion


class _AppsProxy:
    @staticmethod
    def get_model(app_label, model_name):
        if app_label == "referentials" and model_name == "ReferentialItem":
            return ReferentialItem
        if app_label == "referentials" and model_name == "ReferentialCriterion":
            return ReferentialCriterion
        raise LookupError(f"Unknown model {app_label}.{model_name}")


class ReferentialCriteriaBackfillTests(TestCase):
    def test_backfill_creates_ordered_codes_from_item_criteria(self):
        migration_module = importlib.import_module(
            "apps.referentials.migrations.0013_backfill_referential_criteria"
        )
        org = Organisation.objects.create(name="Org Backfill")
        ref = Referential.objects.create(organisation=org, name="Ref", source_ref="SRC")
        item = ReferentialItem.objects.create(
            organisation=org,
            referential=ref,
            code="C1",
            title="Analyser",
            evaluation_criteria=[
                "Les informations necessaires sont recueillies",
                {"label": "Les risques professionnels sont evalues"},
            ],
        )

        migration_module.backfill_criteria(_AppsProxy(), None)

        rows = list(
            ReferentialCriterion.objects.filter(referential_item=item).order_by("order_index")
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].code, "C1.1")
        self.assertEqual(rows[1].code, "C1.2")
        self.assertEqual(rows[0].label, "Les informations necessaires sont recueillies")
        self.assertEqual(rows[1].label, "Les risques professionnels sont evalues")
