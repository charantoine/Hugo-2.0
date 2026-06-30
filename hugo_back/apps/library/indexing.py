"""Document indexing helpers — chunking with safety limits."""
from __future__ import annotations

import logging

from django.conf import settings

from apps.library.chunking import split_into_chunks
from apps.library.models import Document, DocumentChunk

logger = logging.getLogger(__name__)

DEFAULT_MAX_INDEX_CHARS = 1_500_000
DEFAULT_MAX_CHUNKS = 400
DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 50


def _max_index_chars() -> int:
    return int(getattr(settings, "LIBRARY_MAX_INDEX_CHARS", DEFAULT_MAX_INDEX_CHARS))


def _max_chunks() -> int:
    return int(getattr(settings, "LIBRARY_MAX_CHUNKS_PER_DOCUMENT", DEFAULT_MAX_CHUNKS))


def prepare_source_text_for_index(text: str) -> tuple[str, bool]:
    """Truncate oversized text before chunking. Returns (text, was_truncated)."""
    cleaned = (text or "").strip()
    limit = _max_index_chars()
    if len(cleaned) <= limit:
        return cleaned, False
    logger.warning("Document source_text truncated for indexing (%s > %s chars)", len(cleaned), limit)
    return cleaned[:limit], True


def index_document_chunks(
    doc: Document,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> dict:
    """
    Rebuild DocumentChunk rows from doc.source_text.
    Returns summary dict: quality_flag, chunks_count, truncated.
    """
    text, truncated = prepare_source_text_for_index(doc.source_text or "")
    if not text:
        doc.quality_flag = "LOW_TEXT"
        doc.extracted_chars = 0
        doc.chunks_count = 0
        doc.save(update_fields=["quality_flag", "extracted_chars", "chunks_count", "updated_at"])
        DocumentChunk.objects.filter(document=doc).delete()
        return {"quality_flag": "LOW_TEXT", "chunks_count": 0, "truncated": False}

    DocumentChunk.objects.filter(document=doc).delete()
    chunks = split_into_chunks(text, chunk_size=chunk_size, overlap=overlap)
    max_allowed = _max_chunks()
    chunks_capped = len(chunks) > max_allowed
    if chunks_capped:
        logger.warning(
            "Document %s chunk count capped (%s > %s)",
            doc.id,
            len(chunks),
            max_allowed,
        )
        chunks = chunks[:max_allowed]

    # Snapshot doc.meta into each chunk at index time only. PATCH on Document.meta
    # (e.g. trainer_reliability) does not update existing chunks — reindex required for RAG scoring.
    document_meta = dict(doc.meta or {})
    for i, content in enumerate(chunks):
        DocumentChunk.objects.create(
            document=doc,
            content=content,
            meta={
                "index": i,
                "document_meta": document_meta,
                "quality_flag": doc.quality_flag,
            },
        )
    doc.extracted_chars = len(text)
    doc.chunks_count = len(chunks)
    doc.quality_flag = "OK"
    doc.save(update_fields=["extracted_chars", "chunks_count", "quality_flag", "updated_at"])
    return {
        "quality_flag": "OK",
        "chunks_count": len(chunks),
        "truncated": truncated,
        "chunks_capped": chunks_capped,
    }
