"""Rule-based extraction helpers for personal information and simple confidence.

These heuristics will evolve, but give us a baseline before ML integration.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from .schema import Personal

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(\+?\d[\d\s().-]{7,}\d)",  # very permissive, cleaned later
)
NAME_RE = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$")  # Title-case full name


def extract_personal(lines: List[str]) -> Tuple[Personal, float]:
    """Return Personal info + naive confidence (0-1).

    Strategy:
    • Scan first 20 lines for e-mail / phone using regex.
    • Full name guessed from first non-empty Title-case line that isn't e-mail/phone.
    • Confidence = (found_fields / 3).
    """
    email = None
    phone = None
    full_name = None

    top = lines[:20]
    for line in top:
        if email is None:
            m = EMAIL_RE.search(line)
            if m:
                email = m.group(0)
                continue
        if phone is None:
            m = PHONE_RE.search(line)
            if m:
                # normalise: collapse spaces, retain + and digits
                digits = re.sub(r"[^+\d]", "", m.group(0))
                phone = digits
                continue
    # Name detection after email/phone removal
    for line in top:
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        text = line.strip()
        if NAME_RE.match(text):
            full_name = text
            break

    found = sum(1 for x in (full_name, email, phone) if x)
    confidence = found / 3.0  # simple ratio

    personal = Personal(full_name=full_name, email=email, phone=phone)
    return personal, confidence 