"""Tasks: index document (chunks)."""
from celery import shared_task
from django.db import transaction


@shared_task
def index_document(document_id):
    """Best-effort index: extract text, create chunks. Run async."""
    from .models import Document, DocumentChunk
    try:
        doc = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        return
    with transaction.atomic():
        text = getattr(doc, "_extracted_text", "") or ""
        if not text:
            doc.quality_flag = "LOW_TEXT"
            doc.extracted_chars = 0
            doc.chunks_count = 0
            doc.save()
            return
        chunk_size = 500
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - 50)]
        DocumentChunk.objects.filter(document=doc).delete()
        for i, c in enumerate(chunks):
            DocumentChunk.objects.create(document=doc, content=c, meta={"index": i})
        doc.extracted_chars = len(text)
        doc.chunks_count = len(chunks)
        doc.quality_flag = "OK"
        doc.save()
