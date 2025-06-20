from __future__ import annotations

import re
from typing import Dict, List


_SECTION_HEADER_RE = re.compile(r"^(experience|work\s+history|employment|education|skills?|projects?|certifications?|awards?)[:]?$", re.I)


def segment_sections(lines: List[str]) -> Dict[str, List[str]]:
    """Group lines into high-level résumé sections based on heading heuristics."""
    sections: Dict[str, List[str]] = {}
    current_section = "header"
    sections[current_section] = []

    for line in lines:
        if _SECTION_HEADER_RE.match(line.strip()):
            current_section = _SECTION_HEADER_RE.match(line.strip()).group(1).lower()
            sections.setdefault(current_section, [])
            continue
        sections[current_section].append(line)
    return sections 