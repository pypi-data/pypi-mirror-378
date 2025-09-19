from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


class PluginBase(ABC):
    """Base class for JRA plugins.

    Subclasses may override optional methods when applicable (e.g., Qt plugin).
    """

    name: str = "plugin"

    @abstractmethod
    def seeds(self, *, stage_root: str) -> Iterable[str]:
        """Return glob patterns for additional files to seed dependency resolution."""

    def prune_patterns(self) -> Iterable[str]:
        """Regexes to exclude while building the dependency closure."""
        return []

    def classify_plugin(self, path: Path) -> Optional[str]:
        """Return a category name for a plugin file (for placement), or None."""
        return None

    def qml_roots(self, stage_root: str) -> List[Path]:
        """Return QML root directories (absolute or relative to stage_root)."""
        return []

    def asset_seeds(self, *, stage_root: str) -> Iterable[str]:
        """Return additional non-DSO asset patterns (e.g., QML trees)."""
        return []


@dataclass
class PluginResult:
    seeds: List[str]
    prunes: List[str]
