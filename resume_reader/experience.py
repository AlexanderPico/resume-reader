"""Heuristic extraction for experience and education sections.

Very naive implementation: looks for date ranges (YYYY or Mon YYYY) to split
entries and picks nearby lines for title, company, degree etc.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from .schema import EducationItem, ExperienceItem

# Regex patterns -------------------------------------------------------------
YEAR_RE = r"(19|20)\d{2}"
DATE_RANGE_RE = re.compile(
    rf"{YEAR_RE}(?:\s*[–-]\s*(?:{YEAR_RE}|present|current|ongoing))",
    re.I,
)
MONTH_ABBR = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
MONTH_FULL = "january|february|march|april|may|june|july|august|september|october|november|december"
MONTH_RANGE_RE = re.compile(
    rf"(?:{MONTH_ABBR}|{MONTH_FULL})\s+{YEAR_RE}\s*[–-]\s*(?:{MONTH_ABBR}|{MONTH_FULL})?\s*(?:{YEAR_RE}|present|current)",
    re.I,
)

DEGREE_KEYWORDS = re.compile(
    r"(bachelor|master|mba|phd|doctor|licen[cs]e|b\.sc|m\.sc|ba|ma)", re.I
)


# Helpers --------------------------------------------------------------------

def _clean(text: str) -> str:
    return " ".join(text.strip().split())


def _is_valid_company(name: str | None) -> bool:
    """Return True if *name* looks like an organization/company string."""
    if not name:
        return False
    if re.search(r"(inc\.?|llc|corp\.?|institute|institutes|hospital|consortium|laboratories|company|solutions|systems|partners|technologies|gladstone|consortium)", name, re.I):
        return True
    # Accept if <=4 words and each starts with capital
    words = name.split()
    if 0 < len(words) <= 8 and all((not w[0].isalpha()) or w[0].isupper() or w.lower() in {"for", "of", "the", "and"} for w in words):
        return True
    return False


def extract_experience(lines: List[str]) -> Tuple[List[ExperienceItem], float]:
    """Return list of ExperienceItem and confidence.

    Strategy: treat any line with a date-range regex as a boundary marker.
    The preceding line is assumed to be "Title, Company" or "Title at Company".
    Description lines follow until next date marker.
    """
    items: List[ExperienceItem] = []
    i = 0
    last_company: str | None = None

    while i < len(lines):
        line = lines[i]
        if DATE_RANGE_RE.search(line) or MONTH_RANGE_RE.search(line):
            date_match = DATE_RANGE_RE.search(line) or MONTH_RANGE_RE.search(line)
            date_range = date_match.group(0) if date_match else ""

            # Determine start / end -------------------------------------------------
            if "–" in date_range:
                start_raw, end_raw = [s.strip() for s in date_range.split("–", 1)]
            elif "-" in date_range:
                start_raw, end_raw = [s.strip() for s in date_range.split("-", 1)]
            else:
                start_raw, end_raw = date_range.strip(), None

            # Expand start date with month if present in line
            month_match = re.search(rf"({MONTH_FULL}|{MONTH_ABBR})\s+{YEAR_RE}", line, re.I)
            start_str = month_match.group(0) if month_match else start_raw
            end_str = end_raw

            # --- look backwards for title & company ------------------------------
            title: str | None = None
            company: str | None = None

            cand_lines: list[str] = []
            for k in range(1, 13):
                if i - k < 0:
                    break
                cand = _clean(lines[i - k])
                if cand:
                    cand_lines.append(cand)

            if cand_lines:
                JOB_TITLE_KEYWORDS = (
                    r"director|engineer|scientist|fellow|manager|leader|president|developer|investigator|administrator|admin|consultant|analyst|officer"
                )

                # Choose first candidate containing job keyword as title, else fallback to first
                for cand in cand_lines:
                    if re.search(JOB_TITLE_KEYWORDS, cand, re.I):
                        title = cand
                        break
                else:
                    title = cand_lines[0]

                # Remaining candidates potentially include company (exclude title)
                for cand in cand_lines:
                    if cand == title:
                        continue
                    if re.search(r"(inc\.\?|llc|corp\.\?|institute|institutes|university|company|lab|labs|hospital|school|center|centre|resource)", cand, re.I):
                        company = cand
                        break

                # Fallback: if still not set, take the first candidate before title line if available
                if company is None:
                    idx_title = cand_lines.index(title)
                    if idx_title + 1 < len(cand_lines):
                        company = cand_lines[idx_title + 1]

            # Refine splitting of title & company --------------------------------------------------
            if title and " at " in title.lower():
                parts = title.split(" at ", 1)
                title, company = map(_clean, parts)
            elif title and "," in title and (company is None):
                # Comma may just separate multiple roles, so keep full as title
                pass

            # Further clean title – remove prefixes or context before the job keyword
            if title:
                # If colon present, prefer substring after colon when it contains job keywords
                if ":" in title:
                    after_colon = title.split(":", 1)[1].strip()
                    if re.search(JOB_TITLE_KEYWORDS, after_colon, re.I):
                        title = after_colon
                # Could add further cleaning but leave as-is if no colon pattern matched

            # --- look ahead for location line ------------------------------------
            location: str | None = None
            if i + 1 < len(lines):
                next_line = _clean(lines[i + 1])
                # Location lines often contain comma and country/state identifiers
                if re.search(r",\s*(?:[A-Z][a-z]{2,}|United|USA|States|Canada|Kingdom)", next_line):
                    location = next_line

            # Collect description until next date --------------------------------
            desc_lines: List[str] = []
            j = i + 1
            while j < len(lines):
                if DATE_RANGE_RE.search(lines[j]) or MONTH_RANGE_RE.search(lines[j]):
                    break
                # Skip the location line if captured separately
                if _clean(lines[j]) == location:
                    j += 1
                    continue
                desc_lines.append(_clean(lines[j]))
                j += 1

            description = " \n".join([l for l in desc_lines if l]) or None

            # Fallback: reuse last valid company if detection failed or looks invalid
            if company is None or not _is_valid_company(company):
                company = last_company

            exp_item = ExperienceItem(
                title=title,
                company=company,
                location=location,
                start=start_str,
                end=end_str,
                summary="",  # placeholder: description extraction TBD
            )

            items.append(exp_item)

            if _is_valid_company(company):
                last_company = company

            # Continue from next unprocessed line
            i = j
        else:
            i += 1

    # Deduplicate by (title, start) to avoid duplicates
    seen_keys = set()
    unique_items: List[ExperienceItem] = []
    EDUCATION_KEYWORDS = re.compile(r"university|college|school|phd|b\.s|degree", re.I)

    for it in items:
        # Skip duplicates
        key = (it.title, it.start)
        if key in seen_keys:
            continue
        # Heuristic skip education-like entries misclassified as experience
        if EDUCATION_KEYWORDS.search(it.title or "") or EDUCATION_KEYWORDS.search(it.company or ""):
            continue

        seen_keys.add(key)
        unique_items.append(it)

    confidence = min(1.0, len(unique_items) / 3.0) if unique_items else 0.0
    return unique_items, confidence


def extract_education(lines: List[str]) -> Tuple[List[EducationItem], float]:
    """Simple extraction for education entries."""
    items: List[EducationItem] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if DEGREE_KEYWORDS.search(line):
            degree_line = _clean(line)
            degree = degree_line
            institution = None
            start = end = None

            # Check next line for institution or date
            j = i + 1
            if j < len(lines):
                next_line = _clean(lines[j])
                if DATE_RANGE_RE.search(next_line) or MONTH_RANGE_RE.search(next_line):
                    date_match = DATE_RANGE_RE.search(next_line) or MONTH_RANGE_RE.search(next_line)
                    date_range = date_match.group(0)
                    if "–" in date_range:
                        start, end = [s.strip() for s in date_range.split("–", 1)]
                    elif "-" in date_range:
                        start, end = [s.strip() for s in date_range.split("-", 1)]
                    j += 1
                else:
                    institution = next_line
                    j += 1
            # If institution not yet captured and another line available
            if institution is None and j < len(lines):
                institution = _clean(lines[j]) if lines[j].strip() else None
                j += 1

            items.append(
                EducationItem(
                    degree=degree,
                    institution=institution,
                    start=start,
                    end=end,
                )
            )
            i = j
        else:
            i += 1

    confidence = min(1.0, len(items) / 2.0) if items else 0.0
    return items, confidence 