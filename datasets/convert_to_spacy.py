#!/usr/bin/env python
"""Convert raw resume NER corpora into spaCy's binary DocBin format.

Usage
-----
$ python datasets/convert_to_spacy.py \
    --out-dir datasets/spacy \
    --dev-ratio 0.1

Assumes the following raw corpora are already present in the *data/* folder:
    1.  data/Entity Recognition in Resumes.json   (DataTurks format)
    2.  data/545_cvs_train_v2.json                (Doccano format)

A *tags_map.yaml* file in the same folder maps the diverse label sets to a
canonical tag inventory (PERSON, EMAIL, COMPANY, etc.).

The script will emit
    datasets/spacy/train.spacy
    datasets/spacy/dev.spacy
ready to be consumed by ``spacy train``.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml  # PyYAML
import spacy
from spacy.tokens import Doc, DocBin, Span

ROOT = Path(__file__).resolve().parent.parent  # repo root
RAW_DATA_DIR = ROOT / "data"
DEFAULT_CORPORA = [
    RAW_DATA_DIR / "Entity Recognition in Resumes.json",
    RAW_DATA_DIR / "545_cvs_train_v2.json",
]
TAGS_MAP_PATH = Path(__file__).with_name("tags_map.yaml")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_tags_map(path: Path) -> Dict[str, str]:
    """Return dict mapping raw (case-sensitive) labels to canonical labels."""
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def convert_dataturks(record: dict, tag_map: Dict[str, str]) -> Tuple[str, List[Tuple[int, int, str]]]:
    """Convert one DataTurks example into (text, spans).

    DataTurks format::
        {
          "content": "text...",
          "annotation": [
              {"label": ["Skill"], "points": [{"start": 223, "end": 245, "text": "machine learning"}]},
              ...
          ]
        }
    """
    text = record.get("content", "")
    spans: List[Tuple[int, int, str]] = []
    for ann in record.get("annotation", []):
        labels = ann.get("label", [])
        # Take first label only (datasets use singleton list)
        if not labels:
            continue
        raw_label = labels[0]
        label = tag_map.get(raw_label, None)
        if label is None:
            continue  # skip unknown label
        for pt in ann.get("points", []):
            # DataTurks inclusive end index. spaCy expects exclusive.
            start, end = pt["start"], pt["end"] + 1
            spans.append((start, end, label))
    return text, spans


def convert_doccano(record: dict, tag_map: Dict[str, str]) -> Tuple[str, List[Tuple[int, int, str]]]:
    """Convert one Doccano example (545 dataset) into (text, spans)."""
    text = record.get("text", "")
    spans: List[Tuple[int, int, str]] = []
    for start, end, raw_label in record.get("labels", []):
        label = tag_map.get(raw_label, None)
        if label is None:
            continue
        spans.append((int(start), int(end), label))
    return text, spans


FORMATTERS = {
    "Entity Recognition in Resumes.json": convert_dataturks,
    "545_cvs_train_v2.json": convert_doccano,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def iter_examples(tag_map: Dict[str, str]):
    """Yield (text, spans) tuples from the raw corpora."""
    for path in DEFAULT_CORPORA:
        if not path.is_file():
            print(f"[WARN] corpus missing: {path}", file=sys.stderr)
            continue
        text_data = path.read_text(encoding="utf-8").strip()
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            # Assume newline-delimited JSON (one object per line)
            data = [json.loads(line) for line in text_data.splitlines() if line.strip()]
        formatter = FORMATTERS.get(path.name)
        if formatter is None:
            print(f"[WARN] no formatter for {path.name}", file=sys.stderr)
            continue
        for rec in data:
            text, spans = formatter(rec, tag_map)
            if text and spans:
                yield text, spans


def build_docbin(examples, nlp) -> DocBin:
    doc_bin = DocBin(store_user_data=False)
    for text, spans in examples:
        doc: Doc = nlp.make_doc(text)
        ents: List[Span] = []
        for start, end, label in spans:
            if 0 <= start < end <= len(doc.text):
                # Trim leading / trailing whitespace or punctuation from the
                # character offsets so that the resulting span aligns
                # cleanly to tokens and doesn't start/end with whitespace.
                while start < end and doc.text[start].isspace():
                    start += 1
                while start < end and doc.text[end - 1].isspace():
                    end -= 1
                while start < end and doc.text[start] in "(),.;:":
                    start += 1
                while start < end and doc.text[end - 1] in "(),.;:":
                    end -= 1
                if start >= end:
                    continue
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is not None and span.text and not (span.text[0].isspace() or span.text[-1].isspace()):
                    ents.append(span)
        # remove overlaps
        try:
            doc.ents = spacy.util.filter_spans(ents)
        except ValueError:
            # if overlapping still exists, skip example
            continue
        doc_bin.add(doc)
    return doc_bin


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert raw resume NER data to spaCy DocBin format.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for *.spacy files")
    parser.add_argument("--dev-ratio", type=float, default=0.1, help="Fraction of data to use as dev set (default: 0.1)")
    args = parser.parse_args(argv)

    tag_map = load_tags_map(TAGS_MAP_PATH)

    examples = list(iter_examples(tag_map))
    random.shuffle(examples)

    split = int(len(examples) * (1 - args.dev_ratio))
    train_examples = examples[:split]
    dev_examples = examples[split:]

    nlp = spacy.blank("en")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    build_docbin(train_examples, nlp).to_disk(args.out_dir / "train.spacy")
    build_docbin(dev_examples, nlp).to_disk(args.out_dir / "dev.spacy")

    print(f"Wrote {len(train_examples)} training docs and {len(dev_examples)} dev docs to {args.out_dir}.")


if __name__ == "__main__":
    main() 