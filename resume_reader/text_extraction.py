from __future__ import annotations

from pathlib import Path
from typing import List

import pdfplumber


def extract_text(pdf_path: Path) -> List[str]:
    """Extract plain text lines from each page of the PDF.

    Returns a list of strings (one per line) in reading order.
    """
    lines: List[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            # Split into lines and strip whitespace
            for line in page_text.splitlines():
                clean = line.strip()
                if clean:
                    lines.append(clean)
    return lines 