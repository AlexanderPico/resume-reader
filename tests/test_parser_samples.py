"""Dynamic test over any <name>.pdf + <name>_expected.json pairs in tests/data.

If no samples are present (fresh clone), the test module is skipped.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resume_reader.parser import parse
from resume_reader.schema import Resume

# Discover pairs ----------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
PDFS = list(DATA_DIR.glob("*.pdf"))


def param_items() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for pdf in PDFS:
        expected = pdf.with_name(pdf.stem + "_expected.json")
        if expected.exists():
            pairs.append((pdf, expected))
    return pairs


PAIRS = param_items()


@pytest.mark.skipif(
    not PAIRS, reason="No PDF/JSON sample pairs present in tests/data yet."
)
@pytest.mark.parametrize("pdf_path,expected_path", PAIRS)
def test_parse_samples_match_expected(pdf_path: Path, expected_path: Path):
    """Parse *pdf_path* and compare dict output against expected JSON."""
    resume = parse(pdf_path)

    assert isinstance(resume, Resume)

    result_dict = resume.model_dump()
    expected_dict = json.loads(expected_path.read_text())

    assert result_dict == expected_dict, f"Mismatch for {pdf_path.name}" 