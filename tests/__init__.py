import importlib.resources as pkg_resources
from pathlib import Path


def data_path(filename: str) -> Path:
    """Return absolute path to a file inside tests/data."""
    return Path(__file__).parent / "data" / filename 