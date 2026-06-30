"""Multi-tenant isolation for document library APIs."""
from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.library.models import Document, GroupDocument
from apps.referentials.models import Group, GroupMembership


class LibraryMultitenantTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org_a = Organisation.objects.create(name="Org A Library")
        self.org_b = Organisation.objects.create(name="Org B Library")
        self.group_a = Group.objects.create(organisation=self.org_a, name="Group A")
        self.group_b = Group.objects.create(organisation=self.org_b, name="Group B")

        self.trainer_a = User.objects.create_user(
            username="trainer_org_a",
            password="pass",
            organisation=self.org_a,
            role=Role.TRAINER,
        )
        self.trainer_b = User.objects.create_user(
            username="trainer_org_b",
            password="pass",
            organisation=self.org_b,
            role=Role.TRAINER,
        )
        self.learner_a = User.objects.create_user(
            username="learner_org_a",
            password="pass",
            organisation=self.org_a,
            role=Role.LEARNER,
        )
        GroupMembership.objects.create(
            organisation=self.org_a,
            group=self.group_a,
            user=self.learner_a,
        )

        self.doc_a = Document.objects.create(
            organisation=self.org_a,
            title="Document secret Org A",
            source_text="contenu org A",
            meta={"conversation_role": "reference_course"},
        )
        self.doc_b = Document.objects.create(
            organisation=self.org_b,
            title="Document secret Org B",
            source_text="contenu org B",
            meta={"conversation_role": "reference_course"},
        )
        GroupDocument.objects.create(
            organisation=self.org_a,
            group=self.group_a,
            document=self.doc_a,
            status=GroupDocument.Status.ACTIVE,
        )
        GroupDocument.objects.create(
            organisation=self.org_b,
            group=self.group_b,
            document=self.doc_b,
            status=GroupDocument.Status.ACTIVE,
        )

    def test_trainer_b_cannot_read_org_a_group_library(self):
        self.client.force_authenticate(user=self.trainer_b)
        response = self.client.get(reverse("group_library", kwargs={"group_id": self.group_a.id}))
        self.assertIn(response.status_code, {403, 404})

    def test_trainer_a_sees_only_org_a_documents_list(self):
        self.client.force_authenticate(user=self.trainer_a)
        response = self.client.get(reverse("document_list_create"))
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.data]
        self.assertIn("Document secret Org A", titles)
        self.assertNotIn("Document secret Org B", titles)

    def test_trainer_a_library_lists_only_group_a_docs(self):
        self.client.force_authenticate(user=self.trainer_a)
        response = self.client.get(reverse("group_library", kwargs={"group_id": self.group_a.id}))
        self.assertEqual(response.status_code, 200)
        titles = [item["document_title"] for item in response.data.get("items") or []]
        self.assertEqual(titles, ["Document secret Org A"])

    def test_trainer_b_cannot_link_doc_to_foreign_group(self):
        self.client.force_authenticate(user=self.trainer_b)
        response = self.client.post(
            reverse("group_library", kwargs={"group_id": self.group_a.id}),
            {"document_id": str(self.doc_b.id)},
            format="json",
        )
        self.assertIn(response.status_code, {403, 404})

    def test_learner_a_cannot_see_org_b_library(self):
        self.client.force_authenticate(user=self.learner_a)
        response = self.client.get(reverse("group_library", kwargs={"group_id": self.group_b.id}))
        self.assertIn(response.status_code, {403, 404})
