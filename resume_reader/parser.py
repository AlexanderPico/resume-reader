from __future__ import annotations

from pathlib import Path
from typing import Union

from .schema import Resume
from .text_extraction import extract_text
from .segmentation import segment_sections
from .details import extract_personal
from .experience import extract_experience


DEFAULT_CONFIDENCE_THRESHOLD = 0.75


def parse(pdf_path: Union[str, Path], *, use_ml: bool = False) -> Resume:
    """Parse a résumé PDF into a structured :class:`~resume_reader.schema.Resume`.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    use_ml:
        Whether to use machine learning for sectioning.
    Returns
    -------
    Resume
        Parsed structured résumé.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    raw_text = extract_text(pdf_path)
    # Placeholder: ML-based sectioning not yet wired. Accept flag to avoid TypeError.
    if use_ml:
        # Future: dynamic import and fallback
        try:
            from .ml_section import SectionClassifier

            clf = SectionClassifier()
            labels = [clf.predict(line)[0] for line in raw_text]
            sections = {}
            for label, line in zip(labels, raw_text):
                sections.setdefault(label, []).append(line)
        except ImportError:
            # ML stack not installed – fallback gracefully
            sections = segment_sections(raw_text)
    else:
        sections = segment_sections(raw_text)

    # --- rule-based personal info & confidence --------------------------------
    personal, personal_conf = extract_personal(raw_text)

    experience_lines = sections.get("experience", [])

    # ML vs heuristic extraction ------------------------------------------------
    if use_ml:
        try:
            from .ml_experience import extract_experience_ml  # local import to avoid heavy dep when unused

            # If classifier didn't detect an experience section, try full text
            if not experience_lines:
                experience_lines = raw_text

            experience, exp_conf = extract_experience_ml(experience_lines)
        except ImportError:
            # ML deps missing – fallback to heuristics
            if not experience_lines:
                experience_lines = raw_text
            experience, exp_conf = extract_experience(experience_lines)
    else:
        # Fallback: if no "experience" section detected heuristically, attempt extraction from all lines
        if not experience_lines:
            experience_lines = raw_text
        experience, exp_conf = extract_experience(experience_lines)

    # Education extraction (still heuristic; can add ML later) ------------------
    education_lines: list[str] = []
    education: list = []
    edu_conf = 0.0

    # overall confidence: simple average
    confidence_components = [personal_conf, exp_conf, edu_conf]
    confidence = sum(confidence_components) / len(confidence_components)

    resume = Resume(
        personal=personal,
        experience=experience,
        education=education,
        skills=[],
        confidence=confidence,
        needs_review=confidence < DEFAULT_CONFIDENCE_THRESHOLD,
    )

    return resume 