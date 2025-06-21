from __future__ import annotations

"""ML-driven experience extraction using a MiniLM line-role classifier.

The classifier labels each line in the *experience* section as one of
    date, title, company, location, description, other
and then groups consecutive lines into ``ExperienceItem`` objects.

Initially this is zero-shot: we compare sentence-embeddings of the line
against a handful of role prototypes.  The design allows later drop-in of a
fine-tuned model directory by just changing the ``_MODEL_NAME`` constant.
"""

from typing import List, Tuple
import re

from sentence_transformers import SentenceTransformer, util  # type: ignore

from .schema import ExperienceItem

# ---------------------------------------------------------------------------
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# A small set of prototype phrases per role.  Add / replace during fine-tune.
_PROTOS = {
    "date": [
        "Jan 2020 – Present",
        "2011 - 2013",
        "September 2007 – January 2011",
    ],
    "title": [
        "Senior Software Engineer",
        "Research Scientist",
        "Director of Bioinformatics",
    ],
    "company": [
        "Google LLC",
        "Gladstone Institutes",
        "Cytoscape Consortium",
    ],
    "location": [
        "San Francisco, CA, USA",
        "London, United Kingdom",
    ],
    "description": [
        "Developed and maintained software tools for analysis",
        "Led a team of engineers and scientists",
    ],
}

# ---------------------------------------------------------------------------
# Regex helpers for date parsing ------------------------------------------------
YEAR_RE = r"(19|20)\d{2}"
DATE_RANGE_RE = re.compile(
    rf"{YEAR_RE}(?:\s*[–-]\s*(?:{YEAR_RE}|present|current|ongoing))",
    re.I,
)
MONTH_ABBR = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
MONTH_FULL = (
    "january|february|march|april|may|june|july|august|september|october|november|december"
)
MONTH_RANGE_RE = re.compile(
    rf"(?:{MONTH_ABBR}|{MONTH_FULL})\s+{YEAR_RE}\s*[–-]\s*(?:{MONTH_ABBR}|{MONTH_FULL})?\s*(?:{YEAR_RE}|present|current)",
    re.I,
)

# ---------------------------------------------------------------------------
class LineRoleClassifier:
    """Zero-shot role classifier for résumé lines."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(_MODEL_NAME)
        # Pre-encode prototypes for each label
        self._embeds = {
            role: self.model.encode(samples, normalize_embeddings=True)
            for role, samples in _PROTOS.items()
        }

    def predict(self, line: str) -> Tuple[str, float]:
        """Return (best_role, similarity_score) for *line*."""
        emb = self.model.encode(line, normalize_embeddings=True)
        best_role, best_sim = "other", -1.0
        for role, mat in self._embeds.items():
            sim = float(util.cos_sim(emb, mat).max())
            if sim > best_sim:
                best_role, best_sim = role, sim
        return best_role, best_sim


# ---------------------------------------------------------------------------

def _split_date(date_str: str) -> Tuple[str | None, str | None]:
    """Return (start, end) from a raw date-range string."""
    if "–" in date_str:
        return tuple(s.strip() for s in date_str.split("–", 1))  # type: ignore[return-value]
    if "-" in date_str:
        return tuple(s.strip() for s in date_str.split("-", 1))  # type: ignore[return-value]
    return date_str.strip(), None


def extract_experience_ml(lines: List[str]) -> Tuple[List[ExperienceItem], float]:
    """Parse *lines* of an Experience section using the line-role classifier."""

    clf = LineRoleClassifier()

    roles: List[str] = []
    sims: List[float] = []
    for ln in lines:
        role, score = clf.predict(ln)
        roles.append(role)
        sims.append(score)

    items: List[ExperienceItem] = []
    current: dict = {}
    desc_acc: List[str] = []

    for ln, role in zip(lines, roles):
        if role == "date":
            # Finalize previous entry
            if current:
                current["summary"] = " ".join(desc_acc).strip() or ""
                items.append(ExperienceItem(**current))
                current, desc_acc = {}, []

            # Parse date range
            match = DATE_RANGE_RE.search(ln) or MONTH_RANGE_RE.search(ln)
            if match:
                start, end = _split_date(match.group(0))
                current.update({"start": start, "end": end})
            continue

        elif role == "title":
            current["title"] = ln.strip()
        elif role == "company":
            current["company"] = ln.strip()
        elif role == "location":
            current["location"] = ln.strip()
        elif role == "description":
            desc_acc.append(ln.strip())

    # finalize last entry
    if current:
        current["summary"] = " ".join(desc_acc).strip() or ""
        items.append(ExperienceItem(**current))

    # Confidence = average similarity clipped to [0,1]
    conf = sum(sims) / len(sims) if sims else 0.0
    conf = max(0.0, min(conf, 1.0))
    return items, conf 