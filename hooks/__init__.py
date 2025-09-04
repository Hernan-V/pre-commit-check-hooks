"""Pre-commit check hooks package."""

from pathlib import Path

def get_version():
    """Get version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "unknown"

__version__ = get_version()
