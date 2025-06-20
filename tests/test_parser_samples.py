import pytest
import json

from resume_reader.parser import parse
from tests import data_path
from resume_reader.schema import Resume


SAMPLES = [
    "Profile1.pdf",
    "Profile2.pdf",
]


@pytest.mark.parametrize("filename", SAMPLES)
def test_parse_samples(filename):
    pdf_path = data_path(filename)
    expected_path = data_path(filename.replace(".pdf", "_expected.json"))

    resume = parse(pdf_path)

    # Compare full JSON output against expected
    result_dict = resume.model_dump()
    expected_dict = json.loads(expected_path.read_text())

    assert result_dict == expected_dict, f"Mismatch for {filename}" 