from __future__ import annotations

from pathlib import Path
from typing import Union

from .schema import Resume
from .text_extraction import extract_text
from .segmentation import segment_sections
from .classification import classify_sentences


DEFAULT_CONFIDENCE_THRESHOLD = 0.75


def parse(pdf_path: Union[str, Path]) -> Resume:
    """Parse a résumé PDF into a structured :class:`~resume_reader.schema.Resume`.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    Returns
    -------
    Resume
        Parsed structured résumé.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    raw_text = extract_text(pdf_path)
    sections = segment_sections(raw_text)
    labeled = classify_sentences(sections)

    # TODO: deterministic slot filling
    resume = Resume()

    # For MVP, mark as needing review
    resume.needs_review = True
    resume.confidence = 0.0
    return resume 