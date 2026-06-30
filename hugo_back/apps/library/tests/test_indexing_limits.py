"""Tests for document indexing limits and PDF upload."""
import io
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.library.indexing import index_document_chunks, prepare_source_text_for_index
from apps.library.models import Document, DocumentChunk


class IndexingLimitTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Index")
        self.admin = User.objects.create_user(
            username="admin_index",
            password="pass",
            organisation=self.organisation,
            role=Role.ORGADMIN,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_small_text_indexes_without_error(self):
        doc = Document.objects.create(
            organisation=self.organisation,
            title="Petit doc",
            source_text="Contenu court pour chunking. " * 10,
        )
        result = index_document_chunks(doc, chunk_size=100, overlap=10)
        self.assertEqual(result["quality_flag"], "OK")
        self.assertGreater(result["chunks_count"], 0)
        self.assertEqual(DocumentChunk.objects.filter(document=doc).count(), result["chunks_count"])

    @override_settings(LIBRARY_MAX_CHUNKS_PER_DOCUMENT=5)
    def test_heavy_doc_caps_chunks(self):
        doc = Document.objects.create(
            organisation=self.organisation,
            title="Gros doc",
            source_text=("motclef procedure tableau " * 50 + " ") * 200,
        )
        result = index_document_chunks(doc, chunk_size=200, overlap=20)
        self.assertEqual(result["quality_flag"], "OK")
        self.assertLessEqual(result["chunks_count"], 5)
        self.assertTrue(result.get("chunks_capped"))

    @override_settings(LIBRARY_MAX_INDEX_CHARS=500)
    def test_prepare_source_text_truncates(self):
        text, truncated = prepare_source_text_for_index("x" * 2000)
        self.assertTrue(truncated)
        self.assertEqual(len(text), 500)

    @override_settings(LIBRARY_MAX_INDEX_CHARS=50_000, LIBRARY_MAX_CHUNKS_PER_DOCUMENT=20)
    def test_massive_simulated_pdf_text_respects_limits_without_exception(self):
        """Simule un PDF volumineux via source_text très long (pas de fichier binaire en CI)."""
        huge_text = ("procedure tableau electrique consignation verification norme nf " * 800) + "\n"
        self.assertGreater(len(huge_text), 50_000)
        doc = Document.objects.create(
            organisation=self.organisation,
            title="PDF simulé volumineux",
            source_text=huge_text,
            file_path="cours_simule.pdf",
        )
        result = index_document_chunks(doc, chunk_size=500, overlap=50)
        self.assertEqual(result["quality_flag"], "OK")
        self.assertLessEqual(result["chunks_count"], 20)
        self.assertTrue(result.get("truncated") or result.get("chunks_capped"))
        self.assertEqual(
            DocumentChunk.objects.filter(document=doc).count(),
            result["chunks_count"],
        )
        doc.refresh_from_db()
        self.assertLessEqual(doc.extracted_chars, 50_000)
        self.assertLessEqual(doc.chunks_count, 20)

    def test_create_index_api_flow(self):
        r = self.client.post(
            reverse("document_list_create"),
            {"title": "API doc", "source_text": "procedure verification tableau electrique " * 8},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        doc_id = r.data["id"]
        r2 = self.client.post(reverse("document_index", kwargs={"document_id": doc_id}), {}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertGreater(r2.data["chunks_count"], 0)

    def test_invalid_meta_returns_400(self):
        r = self.client.post(
            reverse("document_list_create"),
            {
                "title": "Bad meta",
                "source_text": "texte",
                "meta": {"conversation_role": "not_a_role"},
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400)

    @mock.patch("apps.library.views.extract_pdf_text")
    def test_pdf_upload_and_index(self, mock_extract):
        mock_extract.return_value = "procedure tableau electrique verification mise sous tension"
        pdf_bytes = b"%PDF-1.4 fake"
        upload = io.BytesIO(pdf_bytes)
        upload.name = "cours.pdf"
        r = self.client.post(
            reverse("document_upload"),
            {
                "file": upload,
                "title": "Cours PDF",
                "meta": '{"conversation_role":"reference_course"}',
            },
            format="multipart",
        )
        self.assertEqual(r.status_code, 201, r.content)
        doc_id = r.data["id"]
        r2 = self.client.post(reverse("document_index", kwargs={"document_id": doc_id}), {}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertGreater(r2.data["chunks_count"], 0)
