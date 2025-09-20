import os
from pathlib import Path
from typing import List, Optional, Dict

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.plugins.loader import load_plugins
from justrunalready.resolve import resolve_closure_macos
from justrunalready.platforms.base import PlatformBase
from justrunalready.inspectors import get_inspector


class MacOSPlatform(PlatformBase):
    """macOS platform bundler."""

    @property
    def name(self) -> str:
        return "macos"

    def bundle(
        self,
        cfg: Config,
        wrap: Optional[str] = None,
        *,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> int:
        app_path = cfg.layout.macos.app_bundle
        frameworks_dir = Path(cfg.layout.macos.frameworks_dir)
        plugins_dir = Path(cfg.layout.macos.plugins_dir or "Contents/PlugIns/index")
        rpaths: List[str] = cfg.layout.macos.rpath or []
        actions = Actions(dry_run=dry_run, verbose=verbose)

        if not app_path.exists():
            print(f"app_bundle not found: {app_path}")
            return 2

        # Load plugins and gather their contributions
        plugins = list(load_plugins(cfg))
        staging_root = cfg.app.staging_root

        # Gather seed patterns from includes and plugins
        seed_patterns = cfg.get_platform_includes("macos")
        for plugin in plugins:
            seed_patterns.extend(list(plugin.seeds(stage_root=str(staging_root))))
        seed_files = glob_many(staging_root, seed_patterns)

        macos_dir = app_path / "Contents/MacOS"
        exe_name = None
        if macos_dir.exists():
            for p in macos_dir.iterdir():
                if p.is_file() and os.access(p, os.X_OK):
                    exe_name = p.name
                    break

            if exe_name is None:
                for p in macos_dir.iterdir():
                    if p.is_file():
                        exe_name = p.name
                        break
        if exe_name is None:
            print("Unable to find main executable in Contents/MacOS")
            return 2
        exe_path = macos_dir / exe_name

        # Resolve dependency closure
        closure = resolve_closure_macos(cfg, app_path, exe_path, seed_files)

        # Gather additional asset files from plugins
        asset_patterns: List[str] = []
        for plugin in plugins:
            asset_patterns.extend(
                list(plugin.asset_seeds(stage_root=str(staging_root)))
            )
        asset_files = glob_many(Path("/"), asset_patterns) if asset_patterns else []

        # Build initial file mappings for closure files
        file_mappings: Dict[Path, Path] = {}
        changes: dict[str, str] = {}

        for src in closure:
            try:
                rel = src.relative_to(app_path)
                # File already in app bundle
                dst = app_path / rel
            except ValueError:
                # File outside app bundle - needs to be copied in
                if src.suffix == ".dylib" or ".framework" in src.name:
                    dst = app_path / frameworks_dir / src.name
                    changes[str(src)] = f"@rpath/{dst.name}"
                else:
                    dst = app_path / plugins_dir / src.name

            file_mappings[src] = dst

        # Add asset files to mappings with a generic default location
        # Plugins will reorganize these through organize_files() if needed
        for f in asset_files:
            # By default, place asset files in frameworks directory
            # Plugins can override this in their organize_files method
            file_mappings[f] = app_path / frameworks_dir / f.name

        # Allow plugins to reorganize files
        for plugin in plugins:
            file_mappings = plugin.organize_files(file_mappings)

        # Copy all files to their destinations and update rpaths
        for src, dst in file_mappings.items():
            if not src.exists():
                continue
            actions.copy_file(src, dst)

            # Set ID and rpaths for dylibs
            if dst.suffix == ".dylib" or ".framework" in dst.name:
                if str(src) in changes:
                    actions.set_id_macos(dst, changes[str(src)])

            # Set rpaths for all binaries
            if (
                dst.suffix in (".dylib", "")
                or ".framework" in dst.name
                or dst == exe_path
            ):
                actions.set_exact_rpaths_macos(dst, rpaths)

        # Get macOS inspector for listing dependencies
        inspector = get_inspector("macos")
        if not inspector:
            print("Warning: macOS inspector not available")
            inspector = None

        # Update install names for dependencies
        for src, dst in file_mappings.items():
            try:
                src.relative_to(app_path)
                # File was already in app bundle, use its location
                p = src
            except ValueError:
                # File was copied, use new location
                p = dst

            if not p.exists() and not actions.dry_run:
                continue

            if inspector:
                deps = inspector.list_needed(p)
            else:
                deps = []
            for dep in deps:
                dep_path = Path(dep)
                actions.change_install_name_macos(p, dep, f"@rpath/{dep_path.name}")
            for old, new in changes.items():
                actions.change_install_name_macos(p, old, new)

        staging_lib = staging_root / "lib"
        if staging_lib.exists():
            for f in sorted(staging_lib.glob("*.dylib")):
                dst = app_path / frameworks_dir / f.name
                actions.copy_file(f, dst)
                actions.set_id_macos(dst, f"@rpath/{dst.name}")
                actions.set_exact_rpaths_macos(dst, rpaths)

        # Process explicit copy mappings using base class method
        # Use project root as source since additional files are typically there
        self.process_copy_mappings(
            cfg, Path.cwd(), app_path, actions, default_dest="Contents/Resources"
        )

        print(f"[macOS] Bundled -> {app_path}")
        return 0
