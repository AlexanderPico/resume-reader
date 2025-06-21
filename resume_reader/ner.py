"""spaCy NER wrapper used by parser when --ml flag is enabled.

Loads the `models/ner/model-best` pipeline (relative to project root) by
default, but you can override by setting the environment variable
``RESUME_READER_NER_MODEL`` or calling :func:`load` manually.
"""
from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache
from typing import List, Dict

import spacy
from spacy.tokens import Doc


@lru_cache(maxsize=1)
def _load_model(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(f"spaCy model not found: {model_path}")
    return spacy.load(str(model_path))


def load(model_path: Path | None = None):
    """Return a cached spaCy pipeline instance."""
    if model_path is None:
        model_path = Path(os.getenv("RESUME_READER_NER_MODEL", "models/ner/model-best"))
    return _load_model(Path(model_path))


def extract(text: str) -> List[Dict]:
    """Return NER spans as list of dicts: {text, label, start, end}."""
    nlp = load()
    doc: Doc = nlp(text)
    return [
        {
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        }
        for ent in doc.ents
    ] 