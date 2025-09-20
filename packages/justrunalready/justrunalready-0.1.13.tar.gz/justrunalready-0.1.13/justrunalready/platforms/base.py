"""Base class for platform bundlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, Set

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

    @abstractmethod
    def verify(self, cfg: Config) -> int:
        """Verify that all dependencies in the bundle are satisfied.

        Args:
            cfg: Configuration object

        Returns:
            0 on success, non-zero on failure
        """
        pass

    @abstractmethod
    def resolve_closure(
        self,
        cfg: Config,
        exe_path: Path,
        seeds: Iterable[Path],
        extra_excludes: Optional[Iterable[str]] = None,
    ) -> Set[Path]:
        """Resolve the dependency closure for the platform.

        Args:
            cfg: Configuration object
            exe_path: Path to the main executable
            seeds: Additional files to include in closure
            extra_excludes: Additional exclusion patterns

        Returns:
            Set of paths to include in the bundle
        """
        pass

    def process_copy_mappings(
        self,
        cfg: Config,
        source_root: Path,
        dest_root: Path,
        actions: Actions,
        default_dest: str = "/",
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
                pattern = spec
                dest_dir = Path(default_dest)

                matched_files = glob_many(source_root, [pattern])
                for src_file in matched_files:
                    if not src_file.exists():
                        continue

                    if dest_dir.is_absolute():
                        dest_dir = (
                            dest_dir.relative_to("/")
                            if str(dest_dir).startswith("/")
                            else dest_dir
                        )

                    dest_path = dest_root / dest_dir / src_file.name
                    actions.copy_file(src_file, dest_path)

            elif isinstance(spec, dict):
                if "source" in spec:
                    source_file = source_root / spec["source"]
                    if not source_file.exists():
                        continue

                    dest = Path(spec.get("dest", spec["source"]))
                    if dest.is_absolute():
                        dest = (
                            dest.relative_to("/") if str(dest).startswith("/") else dest
                        )

                    dest_path = dest_root / dest
                    actions.copy_file(source_file, dest_path)
                else:
                    pattern = spec.get("pattern", "")
                    dest_dir = Path(spec.get("dest", default_dest))

                    matched_files = glob_many(source_root, [pattern])
                    for src_file in matched_files:
                        if not src_file.exists():
                            continue

                        if dest_dir.is_absolute():
                            dest_dir = (
                                dest_dir.relative_to("/")
                                if str(dest_dir).startswith("/")
                                else dest_dir
                            )

                        dest_path = dest_root / dest_dir / src_file.name
                        actions.copy_file(src_file, dest_path)
            else:
                continue
