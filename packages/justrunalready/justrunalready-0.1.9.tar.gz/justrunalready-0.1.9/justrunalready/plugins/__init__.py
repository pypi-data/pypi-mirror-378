from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Dict, Any


class PluginBase(ABC):
    """Base class for JRA plugins.

    Plugins can hook into the bundling process to add files,
    exclude files, and organize files in the bundle.
    """

    name: str = "plugin"

    def seeds(self, *, stage_root: str) -> Iterable[str]:
        """Return glob patterns for additional files to seed dependency resolution."""
        return []

    def prune_patterns(self) -> Iterable[str]:
        """Regexes to exclude while building the dependency closure."""
        return []

    def asset_seeds(self, *, stage_root: str) -> Iterable[str]:
        """Return additional non-DSO asset patterns (e.g., QML trees)."""
        return []

    def organize_files(self, files: Dict[Path, Path]) -> Dict[Path, Path]:
        """Given a mapping of source->dest files, reorganize as needed.

        This allows plugins to change where files are placed in the bundle.
        For example, Qt plugin can organize plugins by category.

        Args:
            files: Dictionary mapping source paths to destination paths

        Returns:
            Modified dictionary with potentially different destination paths
        """
        return files


@dataclass
class PluginResult:
    seeds: List[str]
    prunes: List[str]
