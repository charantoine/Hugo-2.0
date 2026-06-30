from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


class TrainerGroupListTests(TestCase):
    """Formateur : membership suffit ; pas de TutorLearnerLink requis (aligné bibliothèque)."""

    def setUp(self):
        self.client = APIClient()
        self.org = Organisation.objects.create(name="Org Trainer Groups")
        user_model = get_user_model()
        self.trainer = user_model.objects.create_user(
            username="trainer_group_list",
            password="pass",
            organisation=self.org,
            role=Role.TRAINER,
        )
        self.group = Group.objects.create(organisation=self.org, name="G trainer")
        GroupMembership.objects.create(
            organisation=self.org,
            group=self.group,
            user=self.trainer,
        )
        self.client.force_authenticate(user=self.trainer)

    def test_trainer_sees_org_groups_without_tutor_link(self):
        response = self.client.get("/groups/")
        self.assertEqual(response.status_code, 200)
        group_ids = {item["id"] for item in response.data}
        self.assertIn(str(self.group.id), group_ids)
        self.assertFalse(
            TutorLearnerLink.objects.filter(group=self.group, tutor=self.trainer).exists()
        )
