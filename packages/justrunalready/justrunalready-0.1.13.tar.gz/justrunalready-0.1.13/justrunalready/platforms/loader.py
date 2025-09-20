"""Platform plugin loader."""

from importlib.metadata import entry_points
from typing import Dict, Optional

from justrunalready.platforms.base import PlatformBase


def load_platforms() -> Dict[str, PlatformBase]:
    """Load all available platform plugins.

    Returns:
        Dictionary mapping platform names to platform instances.
    """
    platforms: Dict[str, PlatformBase] = {}

    for ep in entry_points(group="justrunalready.platforms"):
        try:
            cls = ep.load()
            platform = cls()
            platforms[platform.name] = platform
        except Exception as e:
            print(f"Warning: Failed to load platform {ep.name}: {e}")
            continue

    return platforms


def get_platform(name: str) -> Optional[PlatformBase]:
    """Get a specific platform by name.

    Args:
        name: Platform name (e.g., 'linux', 'windows', 'macos')

    Returns:
        Platform instance or None if not found.
    """
    platforms = load_platforms()
    return platforms.get(name)
