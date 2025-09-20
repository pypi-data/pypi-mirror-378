import os
import logging
from typing import Optional

try:
    from langchain_core.embeddings import Embeddings  # type: ignore
except Exception:  # pragma: no cover
    class Embeddings:  # type: ignore
        def embed_documents(self, texts):
            raise NotImplementedError

        def embed_query(self, text):
            raise NotImplementedError


class SimpleEmbeddings(Embeddings):
    """
    Minimal, deterministic embedding model that does not require network
    or external downloads. It maps text to a 26-dim vector of normalized
    lowercase character frequencies.
    """

    def _vector(self, text: str):
        counts = [0.0] * 26
        total = 0
        for ch in text.lower():
            if "a" <= ch <= "z":
                idx = ord(ch) - ord("a")
                counts[idx] += 1.0
                total += 1
        if total > 0:
            counts = [c / total for c in counts]
        return counts

    def embed_documents(self, texts):
        return [self._vector(t or "") for t in texts]

    def embed_query(self, text):
        return self._vector(text or "")


def get_embeddings() -> Optional[Embeddings]:
    """
    Returns an Embeddings instance.
    If MAMA_EMBEDDINGS=simple, uses SimpleEmbeddings.
    Otherwise tries HuggingFaceEmbeddings and falls back to SimpleEmbeddings.
    """
    if os.environ.get("MAMA_EMBEDDINGS", "").lower() == "simple":
        return SimpleEmbeddings()

    # Try community HF embeddings first
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore

        return HuggingFaceEmbeddings()
    except Exception as e:
        logging.info(f"Falling back to SimpleEmbeddings: {e}")
        return SimpleEmbeddings()

