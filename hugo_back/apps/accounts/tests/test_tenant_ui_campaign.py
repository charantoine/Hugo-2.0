"""
Campagne API — tenant actif, groupes, memberships, divergences connues UI.

Couvre les régressions observées juin 2026 :
- superadmin sans X-Organisation-Id ne voit pas OF_test_2 ;
- formateur voit GET /groups/ mais pas les learners via dashboard ;
- memberships existent en DB mais liste admin dépend du tenant.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.accounts.seeds import demo_test_2_constants as C
from apps.accounts.seeds.demo_test_2 import run_demo_test_2_seed
from apps.referentials.models import Group, GroupMembership


class TenantUiCampaignApiTests(TestCase):
    """Matrice API minimale rôles × tenant pour OF_test_2."""

    @classmethod
    def setUpTestData(cls):
        cls.result = run_demo_test_2_seed()
        cls.org = Organisation.objects.get(id=cls.result.organisation_id)
        cls.group = Group.objects.get(id=cls.result.group_id)
        cls.User = get_user_model()
        cls.trainer = cls.User.objects.get(username=C.TRAINER_USERNAME)
        cls.tutor = cls.User.objects.get(username=C.TUTOR_USERNAME)
        cls.learner = cls.User.objects.get(username=C.LEARNER_USERNAME)
        demo_org = Organisation.objects.filter(name=C.DEFAULT_SOURCE_ORG_NAME).first()
        if demo_org is None:
            demo_org = Organisation.objects.create(name=C.DEFAULT_SOURCE_ORG_NAME)
        cls.superadmin, _ = cls.User.objects.get_or_create(
            username="campaign.superadmin",
            defaults={
                "role": Role.SUPERADMIN,
                "organisation": demo_org,
                "is_active": True,
            },
        )
        if cls.superadmin.organisation_id != demo_org.id:
            cls.superadmin.organisation = demo_org
            cls.superadmin.save(update_fields=["organisation"])

    def _client_for(self, username):
        client = APIClient()
        client.force_authenticate(user=self.User.objects.get(username=username))
        return client

    def test_personas_get_groups_of_test_2(self):
        for username in (C.LEARNER_USERNAME, C.TUTOR_USERNAME, C.TRAINER_USERNAME):
            client = self._client_for(username)
            response = client.get("/groups/")
            self.assertEqual(response.status_code, 200, msg=username)
            names = [g["name"] for g in response.data]
            self.assertIn(C.GROUP_NAME, names, msg=username)

    def test_trainer_sees_membership_count_via_members_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.trainer)
        response = client.get(f"/groups/{self.group.id}/members/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_trainer_dashboard_learners_empty_without_tutor_link(self):
        """Écart structurel documenté : TRAINER traité comme tuteur pour learner_ids_visible."""
        client = APIClient()
        client.force_authenticate(user=self.trainer)
        response = client.get(f"/dashboard/groups/{self.group.id}/learners/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("learners"), [])

    def test_tutor_dashboard_learners_lists_linked_learner(self):
        client = APIClient()
        client.force_authenticate(user=self.tutor)
        response = client.get(f"/dashboard/groups/{self.group.id}/learners/")
        self.assertEqual(response.status_code, 200)
        usernames = [row["username"] for row in response.data.get("learners", [])]
        self.assertIn(C.LEARNER_USERNAME, usernames)

    def test_superadmin_members_empty_without_tenant_header(self):
        client = APIClient()
        client.force_authenticate(user=self.superadmin)
        response = client.get(f"/groups/{self.group.id}/members/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_superadmin_members_visible_with_of_test_2_header(self):
        client = APIClient()
        client.force_authenticate(user=self.superadmin)
        response = client.get(
            f"/groups/{self.group.id}/members/",
            HTTP_X_ORGANISATION_ID=str(self.org.id),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        member_user_ids = {str(row["user"]) for row in response.data}
        for user in (self.trainer, self.tutor, self.learner):
            self.assertIn(str(user.id), member_user_ids)

    def test_superadmin_users_list_scoped_by_tenant_header(self):
        client = APIClient()
        client.force_authenticate(user=self.superadmin)

        without = client.get("/users/")
        self.assertEqual(without.status_code, 200)
        names_without = {u["username"] for u in without.data}

        with_header = client.get("/users/", HTTP_X_ORGANISATION_ID=str(self.org.id))
        self.assertEqual(with_header.status_code, 200)
        names_with = {u["username"] for u in with_header.data}

        self.assertNotIn(C.LEARNER_USERNAME, names_without)
        self.assertIn(C.LEARNER_USERNAME, names_with)

    def test_group_membership_count_matches_db(self):
        db_count = GroupMembership.objects.filter(group=self.group).count()
        client = APIClient()
        client.force_authenticate(user=self.trainer)
        response = client.get(f"/groups/{self.group.id}/members/")
        self.assertEqual(len(response.data), db_count)

    def test_membership_payload_includes_username_and_role(self):
        client = APIClient()
        client.force_authenticate(user=self.trainer)
        response = client.get(f"/groups/{self.group.id}/members/")
        self.assertEqual(response.status_code, 200)
        by_username = {row["user_username"]: row for row in response.data}
        self.assertIn(C.LEARNER_USERNAME, by_username)
        self.assertEqual(by_username[C.LEARNER_USERNAME]["user_role"], "LEARNER")
        self.assertIn(C.TUTOR_USERNAME, by_username)
        self.assertIn(C.TRAINER_USERNAME, by_username)
