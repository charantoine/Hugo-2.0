import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.exports.models import ExportRun
from apps.hugo.models import HugoSession, Trace
from apps.quality.models import AuditLog
from apps.referentials.models import Group, Referential, ReferentialItem


class ExportRunTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()

        self.org_a = Organisation.objects.create(name="Org A")
        self.org_b = Organisation.objects.create(name="Org B")

        self.user_a = user_model.objects.create_user(
            username="org_admin_a",
            password="pass",
            organisation=self.org_a,
            role=Role.ORGADMIN,
        )
        self.user_b = user_model.objects.create_user(
            username="org_admin_b",
            password="pass",
            organisation=self.org_b,
            role=Role.ORGADMIN,
        )
        self.learner_a = user_model.objects.create_user(
            username="learner_a",
            password="pass",
            organisation=self.org_a,
            role=Role.LEARNER,
        )
        self.learner_b = user_model.objects.create_user(
            username="learner_b",
            password="pass",
            organisation=self.org_b,
            role=Role.LEARNER,
        )

        self.group_a = Group.objects.create(organisation=self.org_a, name="Group A")
        self.group_a_alt = Group.objects.create(organisation=self.org_a, name="Group A Alt")
        self.group_b = Group.objects.create(organisation=self.org_b, name="Group B")

        ref_a = Referential.objects.create(organisation=self.org_a, name="Ref A")
        self.item_a = ReferentialItem.objects.create(
            organisation=self.org_a,
            referential=ref_a,
            code="C1",
            title="Competence 1",
        )

        session_a = HugoSession.objects.create(
            organisation=self.org_a,
            learner=self.learner_a,
            group=self.group_a,
        )
        session_a_alt = HugoSession.objects.create(
            organisation=self.org_a,
            learner=self.learner_a,
            group=self.group_a_alt,
        )
        session_b = HugoSession.objects.create(
            organisation=self.org_b,
            learner=self.learner_b,
            group=self.group_b,
        )

        self.trace_a = Trace.objects.create(
            organisation=self.org_a,
            session=session_a,
            referential_item_id=self.item_a.id,
            payload_structured={"session_id": str(session_a.id), "foo": "bar"},
            validated_at=timezone.now(),
        )
        self.trace_a_alt = Trace.objects.create(
            organisation=self.org_a,
            session=session_a_alt,
            payload_structured={"session_id": str(session_a_alt.id), "foo": "baz"},
        )
        self.trace_b = Trace.objects.create(
            organisation=self.org_b,
            session=session_b,
            payload_structured={"session_id": str(session_b.id), "secret": True},
        )

        Trace.objects.filter(id=self.trace_a_alt.id).update(
            created_at=timezone.now() - timedelta(days=10)
        )
        self.trace_a_alt.refresh_from_db()

        self.client.force_authenticate(user=self.user_a)

    def test_csv_export_returns_attachment_with_default_separator_and_bom(self):
        response = self.client.post("/exports/run/", {"format": "csv"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"\xef\xbb\xbf"))

        decoded = response.content.decode("utf-8-sig")
        lines = [line for line in decoded.split("\n") if line]
        self.assertGreaterEqual(len(lines), 2)
        self.assertIn(";", lines[0])
        self.assertIn(str(self.trace_a.id), decoded)
        self.assertIn(str(self.trace_a_alt.id), decoded)
        self.assertNotIn(str(self.trace_b.id), decoded)

    def test_csv_export_supports_custom_separator_and_no_bom(self):
        response = self.client.post(
            "/exports/run/",
            {"format": "csv", "separator": ",", "include_bom": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.content.startswith(b"\xef\xbb\xbf"))
        first_line = response.content.decode("utf-8").split("\n", 1)[0]
        self.assertIn(",", first_line)

    def test_json_export_returns_trace_rich_payloads(self):
        response = self.client.post("/exports/run/", {"format": "json"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])

        payload = json.loads(response.content.decode("utf-8"))
        self.assertEqual(payload["schema"], "trace_rich_v1")
        trace_ids = {item["trace_id"] for item in payload["traces"]}
        self.assertIn(str(self.trace_a.id), trace_ids)
        self.assertIn(str(self.trace_a_alt.id), trace_ids)
        self.assertNotIn(str(self.trace_b.id), trace_ids)

    def test_group_filter_limits_export(self):
        response = self.client.post(
            "/exports/run/",
            {"format": "json", "group_ids": [str(self.group_a.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content.decode("utf-8"))
        trace_ids = {item["trace_id"] for item in payload["traces"]}
        self.assertEqual(trace_ids, {str(self.trace_a.id)})

    def test_period_filter_limits_export(self):
        today = timezone.now().date().isoformat()
        response = self.client.post(
            "/exports/run/",
            {"format": "json", "period": {"from": today, "to": today}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content.decode("utf-8"))
        trace_ids = {item["trace_id"] for item in payload["traces"]}
        self.assertIn(str(self.trace_a.id), trace_ids)
        self.assertNotIn(str(self.trace_a_alt.id), trace_ids)

    def test_invalid_format_returns_400(self):
        response = self.client.post("/exports/run/", {"format": "xml"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_period_returns_400(self):
        response = self.client.post(
            "/exports/run/",
            {"format": "json", "period": {"from": "bad-date"}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_group_ids_returns_400(self):
        response = self.client.post(
            "/exports/run/",
            {"format": "json", "group_ids": ["not-a-uuid"]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_audit_log_is_created_for_export_run(self):
        before = AuditLog.objects.filter(
            organisation=self.org_a,
            action="export_run",
        ).count()
        response = self.client.post("/exports/run/", {"format": "json"}, format="json")
        self.assertEqual(response.status_code, 200)
        after = AuditLog.objects.filter(
            organisation=self.org_a,
            action="export_run",
        ).count()
        self.assertEqual(after, before + 1)

    def test_cross_tenant_isolation_user_b_sees_only_org_b(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.post("/exports/run/", {"format": "json"}, format="json")
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content.decode("utf-8"))
        trace_ids = {item["trace_id"] for item in payload["traces"]}
        self.assertEqual(trace_ids, {str(self.trace_b.id)})

    def test_download_endpoint_replays_export_from_run_params(self):
        run = ExportRun.objects.create(
            organisation=self.org_a,
            params={
                "format": "json",
                "period": {"from": None, "to": None},
                "group_ids": [str(self.group_a.id)],
                "separator": ";",
                "include_bom": True,
            },
            file_path="",
        )
        response = self.client.get(f"/exports/download/{run.id}/")
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content.decode("utf-8"))
        trace_ids = {item["trace_id"] for item in payload["traces"]}
        self.assertEqual(trace_ids, {str(self.trace_a.id)})

    def test_metadata_only_returns_run_metadata_instead_of_file(self):
        response = self.client.post(
            "/exports/run/?metadata_only=true",
            {"format": "csv"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("application/json", response["Content-Type"])
        payload = response.json()
        self.assertTrue(payload["metadata_only"])
        self.assertEqual(payload["mode"], "sync")
        self.assertEqual(payload["format"], "csv")
        self.assertTrue(payload["download_url"].startswith("/exports/download/"))
        self.assertTrue(payload["run_id"])
