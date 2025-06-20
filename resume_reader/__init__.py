from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("resume-reader")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+local"

from .schema import Resume  # noqa: F401
from .parser import parse  # noqa: F401 