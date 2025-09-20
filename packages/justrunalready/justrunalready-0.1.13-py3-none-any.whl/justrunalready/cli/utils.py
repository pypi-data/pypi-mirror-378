"""Shared utilities for CLI commands."""

import sys


def get_platform_name(platform: str) -> str:
    """Normalize platform name.

    Args:
        platform: Platform name or 'auto' for auto-detection

    Returns:
        Normalized platform name ('linux', 'macos', or 'windows')
    """
    platform = platform.lower()

    if platform == "auto":
        if sys.platform.startswith("linux"):
            return "linux"
        elif sys.platform == "darwin":
            return "macos"
        elif sys.platform.startswith("win"):
            return "windows"
        else:
            return sys.platform

    if platform in ("darwin", "mac"):
        return "macos"
    elif platform.startswith("win"):
        return "windows"
    elif platform.startswith("linux"):
        return "linux"

    return platform
