#!/usr/bin/env python
"""Train a spaCy NER model on the DocBin files created earlier.

Example
-------
$ python scripts/train_ner.py \
    --train-path datasets/spacy/train.spacy \
    --dev-path   datasets/spacy/dev.spacy   \
    --output-dir models/ner

The script autogenerates a minimal spaCy config (based on the `config_basic` 
recipe), trains until convergence and saves the best pipeline in *output-dir*.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import spacy
import yaml
SCRIPT_DIR = Path(__file__).resolve().parent
TAGS_MAP_PATH = SCRIPT_DIR.parent / "datasets" / "tags_map.yaml"
def _load_tags() -> dict:
    return yaml.safe_load(TAGS_MAP_PATH.read_text())


def run(cmd: list[str]):
    r = subprocess.run(cmd, check=True)
    return r.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description="Train spaCy NER model.")
    parser.add_argument("--train-path", type=Path, required=True)
    parser.add_argument("--dev-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gpu", type=int, default=-1, help="GPU ID or -1 for CPU")
    args = parser.parse_args(argv)

    # Build a temporary config using spaCy's quickstart recipe.
    config_path = args.output_dir / "config_auto.cfg"
    args.output_dir.mkdir(parents=True, exist_ok=True)

    run([
        sys.executable,
        "-m",
        "spacy",
        "init",
        "config",
        str(config_path),  # positional output file
        "--lang",
        "en",
        "--pipeline",
        "ner",
        "--optimize",
        "efficiency",
        "--force",
    ])

    # Append paths to training data into the config.
    cfg = spacy.util.load_config(config_path)
    cfg["paths"] = {
        "train": str(args.train_path),
        "dev": str(args.dev_path),
        "vectors": "",
        "init_tok2vec": "",
    }
    # Remove interpolation placeholders to appease config validation
    if "initialize" in cfg:
        cfg["initialize"]["vectors"] = None
        cfg["initialize"]["init_tok2vec"] = None
    cfg.to_disk(config_path)

    # Kick off training
    train_cmd = [
        sys.executable,
        "-m",
        "spacy",
        "train",
        str(config_path),
        "--output",
        str(args.output_dir),
        "--paths.train",
        str(args.train_path),
        "--paths.dev",
        str(args.dev_path),
    ]
    if args.gpu >= 0:
        train_cmd.extend(["--gpu-id", str(args.gpu)])

    run(train_cmd)

    print(f"Training complete. Best model saved under {args.output_dir}/model-best")


if __name__ == "__main__":
    main() 