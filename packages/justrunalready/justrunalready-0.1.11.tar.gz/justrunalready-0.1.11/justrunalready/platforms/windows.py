from pathlib import Path
from typing import Optional, Dict

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.plugins.loader import load_plugins
from justrunalready.resolve import resolve_closure_windows
from justrunalready.platforms.base import PlatformBase


class WindowsPlatform(PlatformBase):
    """Windows platform bundler."""

    @property
    def name(self) -> str:
        return "windows"

    def bundle(
        self,
        cfg: Config,
        wrap: Optional[str] = None,
        *,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> int:
        staging = cfg.app.staging_root
        bin_dir = Path(cfg.layout.windows.bin_dir)
        binary = Path(cfg.layout.windows.binary)

        # Binary is located at staging_root/bin_dir/binary
        exe_path = staging / bin_dir / binary
        if not exe_path.exists():
            print(f"exe not found: {exe_path}")
            return 2
        actions = Actions(dry_run=dry_run, verbose=verbose)

        out_bin = staging / bin_dir
        actions.copy_file(exe_path, out_bin / binary.name)

        # Load plugins and gather their contributions
        plugins = list(load_plugins(cfg))

        # Gather seed patterns from includes and plugins
        seed_patterns = cfg.get_platform_includes("windows")
        for plugin in plugins:
            seed_patterns.extend(list(plugin.seeds(stage_root=str(staging))))
        seed_files = glob_many(staging, seed_patterns)

        # Gather prune patterns from plugins
        prunes: list[str] = []
        for plugin in plugins:
            prunes.extend(list(plugin.prune_patterns()))
        # Resolve dependency closure
        closure = resolve_closure_windows(
            cfg, staging, bin_dir / binary, seed_files, extra_excludes=prunes
        )

        # Build initial file mappings for closure files
        file_mappings: Dict[Path, Path] = {}
        for src in closure:
            try:
                rel = src.relative_to(staging)
            except ValueError:
                # Files outside staging directory - skip them
                continue

            # Determine default destination
            if src.suffix.lower() == ".dll":
                dst = out_bin / src.name
            else:
                dst = staging / rel

            file_mappings[src] = dst

        # Allow plugins to reorganize files
        for plugin in plugins:
            file_mappings = plugin.organize_files(file_mappings)

        # Copy all files to their destinations
        for src, dst in file_mappings.items():
            actions.copy_file(src, dst)

        # Process explicit copy mappings using base class method
        # Use project root as source since additional files are typically there
        self.process_copy_mappings(cfg, Path.cwd(), staging, actions, default_dest="/")

        print(f"[windows] Bundled -> {out_bin}")
        return 0
