"""Shared resolution utilities."""

from __future__ import annotations

import importlib.resources
import re
from pathlib import Path
from typing import Iterable, List


def compile_patterns(patterns: Iterable[str]) -> List[re.Pattern[str]]:
    """Compile string patterns into regex patterns."""
    return [re.compile(p) for p in patterns]


def is_excluded(path: Path, patterns: List[re.Pattern[str]]) -> bool:
    """Check if a path matches any exclusion pattern."""
    sp = path.as_posix()
    return any(p.search(sp) for p in patterns)


def fetch_appimage_excludelist() -> List[str]:
    """Get the AppImage excludelist.

    First tries to use the bundled local copy, then falls back to
    a minimal list if that fails.

    Returns a list of library names that should not be bundled
    as they are expected to be present on the host system.
    """
    try:
        import justrunalready.data

        files = importlib.resources.files(justrunalready.data)
        excludelist_file = files / "appimage_excludelist.txt"
        content = excludelist_file.read_text()

        excludes = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                excludes.append(line)
        return excludes
    except Exception as e:
        print(f"Warning: Could not load AppImage excludelist: {e}")
        return [
            "ld-linux.so.2",
            "ld-linux-x86-64.so.2",
            "libc.so.6",
            "libm.so.6",
            "libdl.so.2",
            "libpthread.so.0",
            "librt.so.1",
            "libresolv.so.2",
        ]
