from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from .parser import parse


@click.group()
def app():
    """resume-reader command-line interface."""


@app.command()
@click.argument("pdf", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write JSON to file instead of stdout")
@click.option("--pretty/--no-pretty", default=True, help="Pretty-print JSON output (default: true)")
def parse_cmd(pdf: Path, output: Optional[Path], pretty: bool):
    """Parse a résumé PDF and emit JSON."""
    resume_obj = parse(pdf)
    json_str = json.dumps(
        resume_obj.model_dump(),
        ensure_ascii=False,
        indent=2 if pretty else None,
    )

    if output:
        output.write_text(json_str, encoding="utf-8")
    else:
        click.echo(json_str)


if __name__ == "__main__":
    app() 