"""Corrupted File Cleaner (cfc) package.

Provides GUI (FileCleanerApp), scanning controller, detectors, and utility CLI tools.
"""
from importlib.metadata import version, PackageNotFoundError
from .gui import main as gui_main  # noqa: F401 (expose gui entry)

try:  # pragma: no cover - simple metadata fetch
	__version__ = version("cfc")
except PackageNotFoundError:  # During local editable development before build metadata exists
	__version__ = "0.1.0"

def get_version() -> str:
	"""Return the distribution version string."""
	return __version__

__all__ = ["gui_main", "__version__", "get_version"]
