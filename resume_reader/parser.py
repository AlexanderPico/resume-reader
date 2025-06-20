from __future__ import annotations

from pathlib import Path
from typing import Union

from .schema import Resume
from .text_extraction import extract_text
from .segmentation import segment_sections
from .details import extract_personal


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

    # --- rule-based personal info & confidence --------------------------------
    personal, personal_conf = extract_personal(raw_text)

    # overall confidence: currently just personal_conf; will combine later
    confidence = personal_conf

    resume = Resume(
        personal=personal,
        experience=[],  # TODO: to be filled by heuristics/ML
        education=[],
        skills=[],
        confidence=confidence,
        needs_review=confidence < DEFAULT_CONFIDENCE_THRESHOLD,
    )

    return resume 