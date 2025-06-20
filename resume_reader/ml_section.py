"""MiniLM sentence-embedding based zero-shot section classifier.

Optional dependency – only imported when ``parse(..., use_ml=True)`` is used.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "sentence-transformers missing; install with `pip install sentence-transformers` or `pip install '.[ml]'`"
    ) from e

# ---------------------------------------------------------------------------
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_LABEL_PROTOTYPES = {
    "experience": [
        "work experience",
        "professional experience",
        "employment history",
        "career summary",
    ],
    "education": [
        "education",
        "academic background",
        "studies",
    ],
    "skill": [
        "skills",
        "technical skills",
        "competencies",
    ],
}


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:  # type: ignore[name-defined]
    return SentenceTransformer(_MODEL_NAME)


class SectionClassifier:
    """Zero-shot classifier using cosine similarity to label prototypes."""

    def __init__(self) -> None:
        self.model = _load_model()
        # Pre-encode prototypes (normalized)
        self._label_emb = {
            label: self.model.encode(samples, normalize_embeddings=True)
            for label, samples in _LABEL_PROTOTYPES.items()
        }

    def predict(self, sentence: str) -> Tuple[str, float]:
        """Return (label, similarity) for *sentence*."""
        emb = self.model.encode(sentence, normalize_embeddings=True)
        best_label, best_sim = "other", -1.0
        for label, mat in self._label_emb.items():
            sim = float(util.cos_sim(emb, mat).max())  # type: ignore[attr-defined]
            if sim > best_sim:
                best_label, best_sim = label, sim
        return best_label, best_sim 