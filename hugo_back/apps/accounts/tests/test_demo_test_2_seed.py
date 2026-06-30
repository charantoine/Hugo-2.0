"""Vérifie les rattachements org / groupe / liens tuteur du seed demo_test_2."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.accounts.seeds import demo_test_2_constants as C
from apps.accounts.seeds.demo_test_2 import run_demo_test_2_seed
from apps.referentials.models import Group, GroupMembership, ReferentialConfig, TutorLearnerLink


class DemoTest2SeedAttachmentsTests(TestCase):
    def setUp(self):
        self.result = run_demo_test_2_seed()
        self.org = Organisation.objects.get(id=self.result.organisation_id)
        self.group = Group.objects.get(id=self.result.group_id)
        self.User = get_user_model()

    def test_users_attached_to_organisation(self):
        for username in (C.LEARNER_USERNAME, C.TUTOR_USERNAME, C.TRAINER_USERNAME):
            user = self.User.objects.get(username=username)
            self.assertEqual(user.organisation_id, self.org.id)

    def test_all_roles_have_group_membership(self):
        for username in (C.LEARNER_USERNAME, C.TUTOR_USERNAME, C.TRAINER_USERNAME):
            user = self.User.objects.get(username=username)
            membership = GroupMembership.objects.get(group=self.group, user=user)
            self.assertEqual(membership.organisation_id, self.org.id)

    def test_tutor_learner_link_exists(self):
        tutor = self.User.objects.get(username=C.TUTOR_USERNAME)
        learner = self.User.objects.get(username=C.LEARNER_USERNAME)
        self.assertTrue(
            TutorLearnerLink.objects.filter(
                organisation=self.org,
                group=self.group,
                tutor=tutor,
                learner=learner,
            ).exists()
        )

    def test_referential_config_on_group(self):
        config = ReferentialConfig.objects.get(group=self.group)
        self.assertEqual(config.referential.source_ref, C.REFERENTIAL_SOURCE_REF)
        self.assertEqual(config.organisation_id, self.org.id)

    def test_get_groups_visible_per_role(self):
        client = APIClient()
        expectations = {
            C.LEARNER_USERNAME: 1,
            C.TUTOR_USERNAME: 1,
            C.TRAINER_USERNAME: 1,
        }
        for username, expected_count in expectations.items():
            user = self.User.objects.get(username=username)
            client.force_authenticate(user=user)
            response = client.get("/groups/")
            self.assertEqual(response.status_code, 200, msg=username)
            self.assertEqual(len(response.data), expected_count, msg=username)
            if expected_count:
                self.assertEqual(response.data[0]["name"], C.GROUP_NAME)

    def test_seed_is_idempotent(self):
        second = run_demo_test_2_seed()
        self.assertEqual(second.organisation_id, self.result.organisation_id)
        self.assertEqual(second.group_id, self.result.group_id)
        self.assertEqual(
            GroupMembership.objects.filter(group=self.group).count(),
            3,
        )
        self.assertEqual(
            TutorLearnerLink.objects.filter(group=self.group).count(),
            1,
        )
