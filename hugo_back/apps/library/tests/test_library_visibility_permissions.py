"""Tests: document visibility (internal_only) and library permissions."""
from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.services.rag_support import select_rag_chunks
from apps.library.models import Document, DocumentChunk, GroupDocument
from apps.library.tests.rag_test_helpers import (
    COMMON_CHUNK_TEXT,
    rag_conversation_decision,
    rag_session,
    rag_teaching_plan,
    rag_turn_state,
)
from apps.referentials.models import Group, GroupMembership


class InternalOnlyVisibilityRagTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Visibility")
        self.group = Group.objects.create(organisation=self.organisation, name="G Vis")

    def _link_chunk(self, doc: Document):
        GroupDocument.objects.create(
            organisation=self.organisation,
            group=self.group,
            document=doc,
            status=GroupDocument.Status.ACTIVE,
        )
        DocumentChunk.objects.create(
            document=doc,
            content=COMMON_CHUNK_TEXT,
            meta={"document_meta": dict(doc.meta or {})},
        )

    def test_internal_only_excluded_from_learner_citable_rag(self):
        internal_doc = Document.objects.create(
            organisation=self.organisation,
            title="Note formateur interne",
            meta={"conversation_role": "reference_course", "visibility": "internal_only"},
        )
        public_doc = Document.objects.create(
            organisation=self.organisation,
            title="Poly apprenant",
            meta={"conversation_role": "support", "visibility": "learner_citable"},
        )
        self._link_chunk(internal_doc)
        self._link_chunk(public_doc)

        session = rag_session(self.organisation.id, self.group.id)
        selections = select_rag_chunks(
            session=session,
            learner_text="procedure tableau electrique consignation verification",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=rag_conversation_decision(),
            limit=5,
        )
        selected_ids = {item.document_id for item in selections}
        self.assertNotIn(str(internal_doc.id), selected_ids)
        if selections:
            self.assertIn(str(public_doc.id), selected_ids)

    def test_internal_only_still_listed_in_group_library_api(self):
        admin = User.objects.create_user(
            username="admin_vis",
            password="pass",
            organisation=self.organisation,
            role=Role.ORGADMIN,
        )
        doc = Document.objects.create(
            organisation=self.organisation,
            title="Interne admin",
            meta={"visibility": "internal_only", "conversation_role": "other"},
        )
        GroupDocument.objects.create(
            organisation=self.organisation,
            group=self.group,
            document=doc,
            status=GroupDocument.Status.ACTIVE,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.get(reverse("group_library", kwargs={"group_id": self.group.id}))
        self.assertEqual(response.status_code, 200)
        titles = [item["document_title"] for item in response.data["items"]]
        self.assertIn("Interne admin", titles)


class LibraryPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.organisation = Organisation.objects.create(name="Org Perm")
        self.group = Group.objects.create(organisation=self.organisation, name="G Perm")
        self.trainer = User.objects.create_user(
            username="trainer_perm",
            password="pass",
            organisation=self.organisation,
            role=Role.TRAINER,
        )
        self.orgadmin = User.objects.create_user(
            username="orgadmin_perm",
            password="pass",
            organisation=self.organisation,
            role=Role.ORGADMIN,
        )
        self.learner = User.objects.create_user(
            username="learner_perm",
            password="pass",
            organisation=self.organisation,
            role=Role.LEARNER,
        )

    def test_trainer_creates_orgadmin_sees_same_library(self):
        self.client.force_authenticate(user=self.trainer)
        meta = {
            "conversation_role": "reference_course",
            "pedagogical_intent": "explanation",
            "visibility": "learner_citable",
        }
        create_resp = self.client.post(
            reverse("document_list_create"),
            {"title": "Cours formateur partagé", "source_text": COMMON_CHUNK_TEXT, "meta": meta},
            format="json",
        )
        self.assertEqual(create_resp.status_code, 201, create_resp.content)
        doc_id = create_resp.data["id"]
        index_resp = self.client.post(reverse("document_index", kwargs={"document_id": doc_id}), {}, format="json")
        self.assertEqual(index_resp.status_code, 200)
        link_resp = self.client.post(
            reverse("group_library", kwargs={"group_id": self.group.id}),
            {"document_id": doc_id},
            format="json",
        )
        self.assertEqual(link_resp.status_code, 201)

        self.client.force_authenticate(user=self.orgadmin)
        list_resp = self.client.get(reverse("group_library", kwargs={"group_id": self.group.id}))
        self.assertEqual(list_resp.status_code, 200)
        items = list_resp.data.get("items") or []
        matched = [item for item in items if item["document_id"] == doc_id]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["document_meta"]["conversation_role"], "reference_course")

    def test_learner_cannot_create_document(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.post(
            reverse("document_list_create"),
            {"title": "Hack", "source_text": "x"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_learner_cannot_link_document_to_group(self):
        self.client.force_authenticate(user=self.orgadmin)
        doc_resp = self.client.post(
            reverse("document_list_create"),
            {"title": "Doc admin", "source_text": "contenu"},
            format="json",
        )
        doc_id = doc_resp.data["id"]

        self.client.force_authenticate(user=self.learner)
        link_resp = self.client.post(
            reverse("group_library", kwargs={"group_id": self.group.id}),
            {"document_id": doc_id},
            format="json",
        )
        self.assertEqual(link_resp.status_code, 403)

    def test_learner_without_membership_cannot_read_library(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(reverse("group_library", kwargs={"group_id": self.group.id}))
        self.assertEqual(response.status_code, 403)

    def test_learner_member_can_read_but_not_write_library(self):
        GroupMembership.objects.create(
            organisation=self.organisation,
            group=self.group,
            user=self.learner,
        )
        self.client.force_authenticate(user=self.orgadmin)
        doc_resp = self.client.post(
            reverse("document_list_create"),
            {"title": "Doc groupe", "source_text": "lecture ok"},
            format="json",
        )
        doc_id = doc_resp.data["id"]
        self.client.post(
            reverse("group_library", kwargs={"group_id": self.group.id}),
            {"document_id": doc_id},
            format="json",
        )

        self.client.force_authenticate(user=self.learner)
        read_resp = self.client.get(reverse("group_library", kwargs={"group_id": self.group.id}))
        self.assertEqual(read_resp.status_code, 200)
        write_resp = self.client.post(
            reverse("group_library", kwargs={"group_id": self.group.id}),
            {"document_id": doc_id},
            format="json",
        )
        self.assertEqual(write_resp.status_code, 403)

    def test_trainer_can_patch_document_meta(self):
        self.client.force_authenticate(user=self.trainer)
        create_resp = self.client.post(
            reverse("document_list_create"),
            {
                "title": "Patch meta",
                "source_text": "texte",
                "meta": {"conversation_role": "support"},
            },
            format="json",
        )
        doc_id = create_resp.data["id"]
        patch_resp = self.client.patch(
            reverse("document_detail", kwargs={"document_id": doc_id}),
            {"meta": {"conversation_role": "reference_course", "pedagogical_intent": "diagnosis"}},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.data["meta"]["conversation_role"], "reference_course")
        self.assertEqual(patch_resp.data["meta"]["pedagogical_intent"], "diagnosis")
