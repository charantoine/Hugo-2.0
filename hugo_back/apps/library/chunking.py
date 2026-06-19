"""Split document source text into overlapping chunks for lexical RAG."""
from typing import List


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunk_size = max(100, min(int(chunk_size), 8000))
    overlap = max(0, min(int(overlap), chunk_size - 1))
    step = max(1, chunk_size - overlap)
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        piece = text[i : i + chunk_size]
        if piece.strip():
            chunks.append(piece)
        i += step
        if i >= n:
            break
    return chunks
