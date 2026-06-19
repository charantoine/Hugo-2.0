from django.contrib import admin

from .models import Document, GroupDocument, DocumentChunk, RagCitation


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organisation", "quality_flag", "chunks_count", "extracted_chars", "created_at")
    list_filter = ("organisation", "quality_flag")
    search_fields = ("title",)


@admin.register(GroupDocument)
class GroupDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "document", "status", "organisation", "created_at")
    list_filter = ("organisation", "group", "status")


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "created_at")
    search_fields = ("document__title",)


@admin.register(RagCitation)
class RagCitationAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "document", "chunk", "score", "organisation", "created_at")
    list_filter = ("organisation",)

