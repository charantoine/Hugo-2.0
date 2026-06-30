from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Organisation
from apps.hugo.models import HugoSession, Trace, TraceCriterionAssessment
from apps.hugo.services.context_builder import build_hugo_context
from apps.referentials.models import (
    ReferentialActivity,
    ReferentialCompetencyTask,
    Group,
    Referential,
    ReferentialTask,
    ReferentialConfig,
    ReferentialCriterion,
    ReferentialItem,
)


class ContextBuilderCriteriaTests(TestCase):
    def setUp(self):
        org = Organisation.objects.create(name="Org Test")
        user_model = get_user_model()
        learner = user_model.objects.create_user(
            username="learner_ctx",
            password="pass",
            organisation=org,
        )
        group = Group.objects.create(organisation=org, name="G1")
        referential = Referential.objects.create(
            organisation=org,
            name="Ref Demo",
            source_ref="RNCP-X",
        )
        ReferentialConfig.objects.create(
            organisation=org,
            group=group,
            referential=referential,
        )
        item = ReferentialItem.objects.create(
            organisation=org,
            referential=referential,
            code="C1",
            title="Analyser",
            block_code="BC01",
            block_label="Preparation",
            evaluation_criteria=["LEGACY_NE_DOIT_PAS_ETRE_UTILISE"],
        )
        criterion_1 = ReferentialCriterion.objects.create(
            organisation=org,
            referential_item=item,
            code="C1.1",
            label="Les informations necessaires sont recueillies",
            order_index=0,
        )
        ReferentialCriterion.objects.create(
            organisation=org,
            referential_item=item,
            code="C1.2",
            label="Les risques professionnels sont evalues",
            order_index=1,
        )
        activity = ReferentialActivity.objects.create(
            organisation=org,
            referential=referential,
            code="A1",
            label="Preparation",
            order_index=0,
        )
        task = ReferentialTask.objects.create(
            organisation=org,
            activity=activity,
            code="T1-1",
            label="Prendre connaissance du dossier",
            order_index=0,
        )
        ReferentialCompetencyTask.objects.create(
            organisation=org,
            referential_item=item,
            task=task,
        )
        session = HugoSession.objects.create(
            organisation=org,
            learner=learner,
            group=group,
        )
        trace = Trace.objects.create(
            organisation=org,
            session=session,
            payload_structured={},
        )
        TraceCriterionAssessment.objects.create(
            organisation=org,
            trace=trace,
            criterion=criterion_1,
            status=TraceCriterionAssessment.CoverageStatus.COVERED,
            confidence=0.9,
        )
        self.session = session

    def test_build_hugo_context_reads_criteria_model_and_coverage(self):
        ctx = build_hugo_context(self.session)
        self.assertTrue(ctx.items_to_focus)
        item = ctx.items_to_focus[0]
        self.assertIn("BC01", item.block_code)
        self.assertIn("C1.1", [c.code for c in item.criteria])
        self.assertNotIn("LEGACY_NE_DOIT_PAS_ETRE_UTILISE", item.evaluation_criteria)
        self.assertIn("C1.1", item.covered_criteria_codes)
        self.assertEqual(item.tasks[0]["task_code"], "T1-1")
        self.assertEqual(item.tasks[0]["activity_code"], "A1")
