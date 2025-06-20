"""Minimal helper to fetch a small slice of public résumé corpora.

This is **NOT** executed by the test-suite or CI; it is an optional tool for
contributors who want to populate `tests/data/` with real PDFs + JSON labels
without committing large binaries to git.

Usage (interactive):

    python -m scripts.fetch_corpus_subset --dest tests/data --take 3 \
        --corpus datasetmaster/resumes

Planned behaviour (to be implemented in Milestone 1):
    1. Resolve the HuggingFace dataset (or other source).
    2. Download at most `--take` examples.
    3. Write each PDF as `<name>.pdf` and its reference JSON as
       `<name>_expected.json`.

For now the script only validates arguments and prints the steps it *would*
perform. This avoids introducing heavy dependencies (e.g. `datasets`) until we
wire them in later.
"""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fetch_corpus_subset",
        description="Download a few public-domain CV PDFs + labelled JSON files.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("tests/data"),
        help="Destination directory (will be created if missing)",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        required=True,
        help="Source corpus identifier (e.g. HuggingFace dataset name)",
    )
    parser.add_argument(
        "--take",
        type=int,
        default=5,
        help="Number of samples to download (default: 5)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dest: Path = args.dest
    dest.mkdir(parents=True, exist_ok=True)

    message = textwrap.dedent(
        f"""
        [DRY-RUN] fetch_corpus_subset would now:
          • Resolve corpus: {args.corpus}
          • Download up to {args.take} samples
          • Write files under: {dest.absolute()}
        ---
        This is a placeholder implementation. The real downloader will arrive
        in Milestone 1 once we add lightweight dataset dependencies.
        """
    )
    print(message)


if __name__ == "__main__":
    main() 