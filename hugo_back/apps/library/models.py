"""
Library: Document, GroupDocument, DocumentChunk (embedding), RagCitation.
Embedding: pgvector VectorField when available, else TextField (JSON).
"""
import uuid
from django.db import models
from django.conf import settings

try:
    from pgvector.django import VectorField as _VectorField
    EmbeddingField = lambda: _VectorField(dimensions=512, null=True, blank=True)
except ImportError:
    EmbeddingField = lambda: models.TextField(null=True, blank=True)


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="documents",
        null=False,
    )
    title = models.CharField(max_length=512)
    source_text = models.TextField(blank=True, default="")
    meta = models.JSONField(default=dict)
    file_path = models.CharField(max_length=512, blank=True)
    extracted_chars = models.PositiveIntegerField(default=0)
    chunks_count = models.PositiveIntegerField(default=0)
    quality_flag = models.CharField(max_length=20, default="OK")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "document"
        ordering = ["-created_at"]


class GroupDocument(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="group_documents",
        null=False,
    )
    group = models.ForeignKey(
        "referentials.Group",
        on_delete=models.CASCADE,
        related_name="library_documents",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="group_documents",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "group_document"
        unique_together = [["group", "document"]]


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    content = models.TextField()
    meta = models.JSONField(default=dict)
    embedding = EmbeddingField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document_chunk"
        ordering = ["created_at"]


class RagCitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="rag_citations",
        null=False,
    )
    message = models.ForeignKey(
        "hugo.HugoMessage",
        on_delete=models.CASCADE,
        related_name="rag_citations",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="rag_citations",
    )
    chunk = models.ForeignKey(
        DocumentChunk,
        on_delete=models.CASCADE,
        related_name="rag_citations",
    )
    score = models.FloatField(default=0.0)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_citation"
        ordering = ["-created_at"]
