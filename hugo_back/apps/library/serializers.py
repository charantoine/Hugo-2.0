from rest_framework import serializers

from .document_meta import (
    prepare_document_meta_for_create,
    prepare_document_meta_for_update,
    validate_document_meta,
)
from .models import Document, GroupDocument

MAX_SOURCE_TEXT_CHARS = 2_000_000


class DocumentListSerializer(serializers.ModelSerializer):
    has_source_text = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "meta",
            "file_path",
            "extracted_chars",
            "chunks_count",
            "quality_flag",
            "has_source_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_has_source_text(self, obj: Document) -> bool:
        return bool((obj.source_text or "").strip())


class DocumentSerializer(serializers.ModelSerializer):
    """POST /documents/ — title + optional source_text (markdown/plain)."""

    source_text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_SOURCE_TEXT_CHARS,
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "source_text",
            "meta",
            "file_path",
            "extracted_chars",
            "chunks_count",
            "quality_flag",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "extracted_chars", "chunks_count", "quality_flag", "created_at", "updated_at"]

    def validate_meta(self, value):
        request = self.context.get("request")
        if self.instance is not None:
            return prepare_document_meta_for_update(self.instance.meta, value)
        if request is not None:
            return prepare_document_meta_for_create(request.user, value)
        return validate_document_meta(value, allow_origin=False)

    def create(self, validated_data):
        request = self.context.get("request")
        meta = validated_data.get("meta")
        if request is not None:
            validated_data["meta"] = prepare_document_meta_for_create(request.user, meta)
        return super().create(validated_data)


class DocumentDetailSerializer(serializers.ModelSerializer):
    """GET/PATCH /documents/{id}/ — full source_text for read/update."""

    source_text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_SOURCE_TEXT_CHARS,
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "source_text",
            "meta",
            "file_path",
            "extracted_chars",
            "chunks_count",
            "quality_flag",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "extracted_chars", "chunks_count", "quality_flag", "created_at", "updated_at"]

    def validate_meta(self, value):
        if self.instance is not None:
            return prepare_document_meta_for_update(self.instance.meta, value)
        return validate_document_meta(value, allow_origin=False)

    def update(self, instance, validated_data):
        if "meta" in validated_data:
            validated_data["meta"] = prepare_document_meta_for_update(
                instance.meta,
                validated_data.get("meta"),
            )
        return super().update(instance, validated_data)


class GroupDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupDocument
        fields = ["id", "group", "document", "status", "created_at"]
        read_only_fields = ["id", "created_at"]
