from __future__ import annotations

import mimetypes
from pathlib import Path


def ingest_document(file_path: str, organisation_id: str, referential_item_id: str = "") -> list[dict]:
    path = Path(file_path)
    if not path.exists():
        return []
    mime, _ = mimetypes.guess_type(str(path))
    if mime == "application/pdf":
        text = _extract_pdf_text(path)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
    return _extract_items_from_text(text, organisation_id, referential_item_id)


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
    except Exception:
        return ""
    chunks: list[str] = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(chunks)


def _extract_items_from_text(text: str, organisation_id: str, referential_item_id: str) -> list[dict]:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    extracted: list[dict] = []
    for line in lines[:20]:
        lowered = line.lower()
        if any(token in lowered for token in ["erreur", "risque"]):
            content_type = "frequent_error"
        elif any(token in lowered for token in ["règle", "regle", "procédure", "procedure"]):
            content_type = "reference_rule"
        elif any(token in lowered for token in ["raisonnement", "analyse", "diagnostic"]):
            content_type = "reasoning_chain"
        else:
            content_type = "mastery_criterion"
        extracted.append(
            {
                "organisation_id": organisation_id,
                "referential_item_id": referential_item_id,
                "content": line,
                "content_type": content_type,
                "source_type": "document_extracted",
                "status": "derived_provisional",
                "confidence_score": 0.5,
                "provenance_note": f"Imported from {Path(referential_item_id or 'document').name}",
            }
        )
    return extracted
