from __future__ import annotations

from typing import Dict, List


_KEYWORDS = {
    "experience": ["developed", "managed", "led", "experience", "responsible"],
    "education": ["university", "bachelor", "master", "phd", "degree"],
    "skill": ["python", "java", "c++", "machine learning", "sql"],
}


def classify_sentences(sections: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Very naive sentence-level classifier assigning lines to tags within sections.

    Returns the same structure for now; will be replaced by ML model.
    """
    # Placeholder – assume segmentation already good
    return sections 