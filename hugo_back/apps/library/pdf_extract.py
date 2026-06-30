"""PDF text extraction for document library ingestion."""
from __future__ import annotations

from pathlib import Path


def extract_pdf_text(path: Path | str) -> str:
    path = Path(path)
    if not path.exists():
        return ""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
    except Exception:
        return ""
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts).strip()
