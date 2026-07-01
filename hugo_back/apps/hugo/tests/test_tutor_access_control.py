from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoMessage, HugoSession, Trace
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


class TutorAccessControlTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organisation.objects.create(name="Org ACL")
        user_model = get_user_model()
        self.tutor = user_model.objects.create_user(
            username="tutor_acl",
            password="pass",
            organisation=self.org,
            role=Role.TUTOR,
        )
        self.learner_linked = user_model.objects.create_user(
            username="learner_linked_acl",
            password="pass",
            organisation=self.org,
            role=Role.LEARNER,
        )
        self.learner_unlinked = user_model.objects.create_user(
            username="learner_unlinked_acl",
            password="pass",
            organisation=self.org,
            role=Role.LEARNER,
        )
        self.group = Group.objects.create(organisation=self.org, name="G ACL")
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group,
            user=self.tutor,
        )
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group,
            user=self.learner_linked,
        )
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group,
            user=self.learner_unlinked,
        )
        TutorLearnerLink.objects.create(
            organisation=self.org,
            group=self.group,
            tutor=self.tutor,
            learner=self.learner_linked,
        )
        self.linked_session = HugoSession.objects.create(
            organisation=self.org,
            group=self.group,
            learner=self.learner_linked,
        )
        self.unlinked_session = HugoSession.objects.create(
            organisation=self.org,
            group=self.group,
            learner=self.learner_unlinked,
        )
        self.linked_trace = Trace.objects.create(
            organisation=self.org,
            session=self.linked_session,
            payload_structured={},
        )
        self.unlinked_trace = Trace.objects.create(
            organisation=self.org,
            session=self.unlinked_session,
            payload_structured={},
        )
        self.client.force_authenticate(user=self.tutor)

    def test_dashboard_learners_lists_only_linked_learners_for_tutor(self):
        response = self.client.get(f"/dashboard/groups/{self.group.id}/learners/")
        self.assertEqual(response.status_code, 200)
        learner_ids = {item["id"] for item in response.data.get("learners", [])}
        self.assertIn(str(self.learner_linked.id), learner_ids)
        self.assertNotIn(str(self.learner_unlinked.id), learner_ids)

    def test_dashboard_timeline_for_unlinked_learner_is_forbidden(self):
        response = self.client.get(
            f"/dashboard/groups/{self.group.id}/learners/{self.learner_unlinked.id}/timeline/"
        )
        self.assertEqual(response.status_code, 403)

    def test_dashboard_timeline_for_linked_learner_is_allowed(self):
        response = self.client.get(
            f"/dashboard/groups/{self.group.id}/learners/{self.learner_linked.id}/timeline/"
        )
        self.assertEqual(response.status_code, 200)

    def test_dashboard_timeline_includes_shared_verbatim_messages_with_variants(self):
        self.linked_session.share_verbatim = True
        self.linked_session.save(update_fields=["share_verbatim"])
        HugoMessage.objects.create(
            organisation=self.org,
            session=self.linked_session,
            role=HugoMessage.Role.LEARNER,
            content="J'ai remplace la prise.",
        )
        HugoMessage.objects.create(
            organisation=self.org,
            session=self.linked_session,
            role=HugoMessage.Role.ASSISTANT,
            content="Version courte",
            assistant_display_variants={
                "short": "Version courte",
                "long": "Version longue",
                "default_variant": "short",
                "available_variants": ["short", "long"],
            },
        )

        response = self.client.get(
            f"/dashboard/groups/{self.group.id}/learners/{self.learner_linked.id}/timeline/"
        )

        self.assertEqual(response.status_code, 200)
        session_payload = response.data["sessions"][0]
        self.assertTrue(session_payload["share_verbatim"])
        self.assertEqual(len(session_payload["messages"]), 2)
        self.assertEqual(
            session_payload["messages"][1]["assistant_display_variants"]["long"],
            "Version longue",
        )

    def test_dashboard_timeline_includes_pilotage_without_prompt_leak(self):
        self.linked_session.share_verbatim = True
        self.linked_session.save(update_fields=["share_verbatim"])
        learner_msg = HugoMessage.objects.create(
            organisation=self.org,
            session=self.linked_session,
            role=HugoMessage.Role.LEARNER,
            content="Merci, je clos.",
            llm_request_payload={
                "turn_state": {
                    "covered_points": ["cause", "action"],
                    "remaining_open_points": [],
                    "learner_help_request": "none",
                    "closure_signal": "explicit",
                    "repetition_signal": "none",
                    "loop_risk": "low",
                    "assistant_meta_leak_risk": "low",
                },
                "conversation_decision": {
                    "pedagogical_move": "assist",
                    "number_of_questions": 0,
                    "primary_intent": "acknowledge_close",
                },
                "system_prompt": "SECRET_PROMPT_MUST_NOT_APPEAR_IN_TIMELINE",
            },
        )
        response = self.client.get(
            f"/dashboard/groups/{self.group.id}/learners/{self.learner_linked.id}/timeline/"
        )
        self.assertEqual(response.status_code, 200)
        sessions = response.data["sessions"]
        session_payload = next(s for s in sessions if s["id"] == str(self.linked_session.id))
        msg = next(m for m in session_payload["messages"] if m["id"] == str(learner_msg.id))
        self.assertIn("pilotage", msg)
        self.assertNotIn("p0_debug", msg)
        self.assertNotIn("turn_state", msg)
        pilotage = msg["pilotage"]
        self.assertEqual(pilotage["decision_move"], "assist")
        self.assertEqual(pilotage["closure_signal"], "explicit")
        self.assertNotIn("system_prompt", msg)
        self.assertNotIn("SECRET_PROMPT", str(msg))

    def test_trace_validation_for_unlinked_learner_is_forbidden(self):
        response = self.client.post(f"/traces/{self.unlinked_trace.id}/validate/")
        self.assertEqual(response.status_code, 403)

    def test_trace_validation_for_linked_learner_is_allowed(self):
        response = self.client.post(f"/traces/{self.linked_trace.id}/validate/")
        self.assertEqual(response.status_code, 200)

    def test_memory_summary_for_linked_learner_session_forbidden_for_tutor(self):
        response = self.client.get(
            f"/hugo/sessions/{self.linked_session.id}/memory-summary/"
        )
        self.assertEqual(response.status_code, 404)
