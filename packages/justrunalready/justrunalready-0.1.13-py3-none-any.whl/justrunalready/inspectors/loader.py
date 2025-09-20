"""Inspector plugin loader."""

from importlib.metadata import entry_points
from typing import Dict, Optional

from justrunalready.inspectors.base import InspectorBase


def load_inspectors() -> Dict[str, InspectorBase]:
    """Load all available inspector plugins.

    Returns:
        Dictionary mapping inspector names to inspector instances.
    """
    inspectors: Dict[str, InspectorBase] = {}

    for ep in entry_points(group="justrunalready.inspectors"):
        try:
            cls = ep.load()
            inspector = cls()
            inspectors[inspector.name] = inspector
        except Exception as e:
            print(f"Warning: Failed to load inspector {ep.name}: {e}")
            continue

    return inspectors


def get_inspector(name: str) -> Optional[InspectorBase]:
    """Get a specific inspector by name.

    Args:
        name: Inspector name (e.g., 'linux', 'windows', 'macos')

    Returns:
        Inspector instance or None if not found.
    """
    inspectors = load_inspectors()
    return inspectors.get(name)
