from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


class GroupVisibilityByTutorLinksTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organisation.objects.create(name="Org Group ACL")
        user_model = get_user_model()
        self.tutor = user_model.objects.create_user(
            username="tutor_group_acl",
            password="pass",
            organisation=self.org,
            role=Role.TUTOR,
        )
        self.learner_linked = user_model.objects.create_user(
            username="learner_group_linked_acl",
            password="pass",
            organisation=self.org,
            role=Role.LEARNER,
        )
        self.learner_unlinked = user_model.objects.create_user(
            username="learner_group_unlinked_acl",
            password="pass",
            organisation=self.org,
            role=Role.LEARNER,
        )
        self.group_linked = Group.objects.create(organisation=self.org, name="G linked")
        self.group_unlinked = Group.objects.create(organisation=self.org, name="G unlinked")
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group_linked,
            user=self.tutor,
        )
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group_linked,
            user=self.learner_linked,
        )
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group_unlinked,
            user=self.tutor,
        )
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group_unlinked,
            user=self.learner_unlinked,
        )
        TutorLearnerLink.objects.create(
            organisation=self.org,
            group=self.group_linked,
            tutor=self.tutor,
            learner=self.learner_linked,
        )
        self.client.force_authenticate(user=self.tutor)

    def test_tutor_only_sees_groups_with_linked_learners(self):
        response = self.client.get("/groups/")
        self.assertEqual(response.status_code, 200)
        group_ids = {item["id"] for item in response.data}
        self.assertIn(str(self.group_linked.id), group_ids)
        self.assertNotIn(str(self.group_unlinked.id), group_ids)

    def test_tutor_can_create_link_when_both_users_are_group_members(self):
        payload = {
            "tutor": str(self.tutor.id),
            "learner": str(self.learner_unlinked.id),
        }
        response = self.client.post(f"/groups/{self.group_unlinked.id}/tutor-links/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            TutorLearnerLink.objects.filter(
                organisation=self.org,
                group=self.group_unlinked,
                tutor=self.tutor,
                learner=self.learner_unlinked,
            ).exists()
        )
