from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Organisation
from apps.referentials.models import (
    Referential,
    ReferentialActivity,
    ReferentialTask,
    ReferentialCompetencyTask,
    ReferentialItem,
)


class ReferentialImportActivitiesTasksTests(APITestCase):
    def setUp(self):
        org = Organisation.objects.create(name="Org Import")
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="admin_import",
            password="pass",
            organisation=org,
            role="ORGADMIN",
        )
        self.client.force_authenticate(user=self.user)

    def test_import_v2_non_regression_items_and_criteria_only(self):
        payload = {
            "name": "Ref Legacy",
            "source_ref": "RNCP-X",
            "items": [
                {
                    "code": "C1",
                    "title": "Competence 1",
                    "criteria": [{"code": "C1.1", "label": "Critere 1"}],
                }
            ],
        }
        response = self.client.post("/referentials/import-v2/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["items_count"], 1)
        self.assertEqual(response.data["activities_count"], 0)
        self.assertEqual(response.data["tasks_count"], 0)

    def test_import_v2_enriched_creates_activities_tasks_and_links(self):
        payload = {
            "name": "Ref Full",
            "source_ref": "RNCP38878",
            "items": [
                {
                    "code": "C1",
                    "title": "Analyser",
                    "block_code": "BC01",
                    "block_label": "Preparation",
                    "criteria": [{"code": "C1.1", "label": "Info recueillie"}],
                    "tasks": ["T1-1", "T1-2"],
                }
            ],
            "activities": [
                {
                    "code": "A1",
                    "label": "Preparation",
                    "order_index": 1,
                    "tasks": [
                        {"code": "T1-1", "label": "Lire dossier", "order_index": 1},
                        {"code": "T1-2", "label": "Chercher infos", "order_index": 2},
                    ],
                }
            ],
            "competency_tasks": [
                {"competency_code": "C1", "task_code": "T1-1"},
                {"competency_code": "C1", "task_code": "T1-2"},
            ],
        }
        response = self.client.post("/referentials/import-v2/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["activities_count"], 1)
        self.assertEqual(response.data["tasks_count"], 2)
        self.assertEqual(ReferentialActivity.objects.count(), 1)
        self.assertEqual(ReferentialTask.objects.count(), 2)
        self.assertEqual(ReferentialCompetencyTask.objects.count(), 2)

    def test_read_endpoints_return_activities_tasks_and_item_links(self):
        ref = Referential.objects.create(
            organisation=self.user.organisation,
            name="Ref Read",
            source_ref="REF",
        )
        item = ReferentialItem.objects.create(
            organisation=self.user.organisation,
            referential=ref,
            code="C1",
            title="Analyser",
            block_code="BC01",
            block_label="Preparation",
        )
        activity = ReferentialActivity.objects.create(
            organisation=self.user.organisation,
            referential=ref,
            code="A1",
            label="Preparation",
            order_index=1,
        )
        task = ReferentialTask.objects.create(
            organisation=self.user.organisation,
            activity=activity,
            code="T1-1",
            label="Lire dossier",
            order_index=1,
        )
        ReferentialCompetencyTask.objects.create(
            organisation=self.user.organisation,
            referential_item=item,
            task=task,
        )

        activities_resp = self.client.get(f"/referentials/{ref.id}/activities/")
        self.assertEqual(activities_resp.status_code, status.HTTP_200_OK)
        activities = activities_resp.data if isinstance(activities_resp.data, list) else activities_resp.data.get("results", [])
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]["code"], "A1")

        tasks_resp = self.client.get(f"/referentials/{ref.id}/activities/{activity.id}/tasks/")
        self.assertEqual(tasks_resp.status_code, status.HTTP_200_OK)
        tasks = tasks_resp.data if isinstance(tasks_resp.data, list) else tasks_resp.data.get("results", [])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["code"], "T1-1")

        item_tasks_resp = self.client.get(f"/referentials/{ref.id}/items/{item.id}/tasks/")
        self.assertEqual(item_tasks_resp.status_code, status.HTTP_200_OK)
        links = item_tasks_resp.data if isinstance(item_tasks_resp.data, list) else item_tasks_resp.data.get("results", [])
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["task_code"], "T1-1")
