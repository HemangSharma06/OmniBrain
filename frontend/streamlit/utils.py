"""Small, side-effect-free helpers used by the Streamlit interface."""

from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def as_list(value: Any) -> list[Any]:
    """Return API values as a list while preserving useful scalar values."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def display_name(item: Any) -> str:
    """Get a readable name from a source or document API value."""
    if isinstance(item, dict):
        for key in ("name", "filename", "source", "file_path", "path"):
            if item.get(key):
                return str(item[key])
    return str(item)


def resolve_image_reference(reference: Any) -> str | None:
    """Resolve an image URL or a backend-created local path."""
    value = reference.get("path") if isinstance(reference, dict) else reference
    if not value:
        return None
    value = str(value)
    if urlparse(value).scheme in {"http", "https"}:
        return value

    image_path = Path(value)
    candidates = [image_path]
    project_root = Path(__file__).resolve().parents[2]
    if not image_path.is_absolute():
        candidates.extend((project_root / image_path, project_root / "data" / image_path))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None