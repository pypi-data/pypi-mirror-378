"""Base class for platform bundlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any

from justrunalready.config import Config
from justrunalready.utils import Actions, glob_many


class PlatformBase(ABC):
    """Base class for platform-specific bundlers."""

    def __init__(self):
        """Initialize the platform bundler."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the platform name (e.g., 'linux', 'windows', 'macos')."""
        pass

    @abstractmethod
    def bundle(
        self,
        cfg: Config,
        wrap: Optional[str] = None,
        *,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> int:
        """Bundle the application for this platform.

        Args:
            cfg: Configuration object
            wrap: Optional wrapper to use
            dry_run: If True, don't actually perform actions
            verbose: If True, print verbose output

        Returns:
            0 on success, non-zero on failure
        """
        pass

    def process_copy_mappings(
        self,
        cfg: Config,
        source_root: Path,
        dest_root: Path,
        actions: Actions,
        default_dest: str = "/"
    ) -> None:
        """Process platform-specific copy mappings.

        Args:
            cfg: Configuration object with get_platform_copies method
            source_root: Root directory to search for source files
            dest_root: Root directory for destination files
            actions: Actions object for copy operations
            default_dest: Default destination directory if not specified
        """
        copy_specs = cfg.get_platform_copies(self.name)

        for spec in copy_specs:
            if isinstance(spec, str):
                # Simple pattern - copy to default destination
                pattern = spec
                dest_dir = Path(default_dest)
            elif isinstance(spec, dict):
                # Mapping with explicit destination
                pattern = spec.get("pattern", "")
                dest_dir = Path(spec.get("dest", default_dest))
            else:
                continue

            # Find files matching the pattern
            matched_files = glob_many(source_root, [pattern])
            for src_file in matched_files:
                if not src_file.exists():
                    continue

                # Determine destination
                if dest_dir.is_absolute():
                    dest_dir = Path(str(dest_dir).lstrip("/"))

                dest_path = dest_root / dest_dir / src_file.name
                actions.copy_file(src_file, dest_path)