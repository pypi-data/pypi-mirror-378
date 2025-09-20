from pathlib import Path
from typing import List, Optional, Dict

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.plugins.loader import load_plugins
from justrunalready.resolve import resolve_closure_linux
from justrunalready.platforms.base import PlatformBase
from justrunalready.utils import run


class LinuxPlatform(PlatformBase):
    """Linux platform bundler."""

    @property
    def name(self) -> str:
        return "linux"

    def bundle(
        self,
        cfg: Config,
        wrap: Optional[str] = None,
        *,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> int:
        staging = cfg.app.staging_root
        staging_abs = staging.resolve()
        out_root = cfg.layout.linux.appdir
        bin_dir = Path(cfg.layout.linux.bin_dir)
        lib_dir = Path(cfg.layout.linux.lib_dir)
        rpaths: List[str] = cfg.layout.linux.rpath or []
        binary = Path(cfg.layout.linux.binary)
        actions = Actions(dry_run=dry_run, verbose=verbose)

        # Binary is located at staging_root/bin_dir/binary
        exe_path = staging_abs / bin_dir / binary
        if not exe_path.exists():
            print(f"binary not found: {exe_path}")
            return 2

        out_bin = out_root / bin_dir
        exe_out = out_bin / binary.name
        actions.copy_file(exe_path, exe_out)

        # Load plugins and gather their contributions
        plugins = list(load_plugins(cfg))

        # Gather seed patterns from includes and plugins
        seed_patterns = cfg.get_platform_includes("linux")
        for plugin in plugins:
            seed_patterns.extend(list(plugin.seeds(stage_root=str(staging_abs))))
        seed_files = glob_many(staging_abs, seed_patterns)

        # Gather prune patterns from plugins
        prunes: List[str] = []
        for plugin in plugins:
            prunes.extend(list(plugin.prune_patterns()))
        # Resolve dependency closure
        closure = resolve_closure_linux(
            cfg, staging, bin_dir / binary, seed_files, extra_excludes=prunes
        )

        # Gather additional asset files from plugins
        asset_patterns: List[str] = []
        for plugin in plugins:
            asset_patterns.extend(list(plugin.asset_seeds(stage_root=str(staging_abs))))
        asset_files = glob_many(Path("/"), asset_patterns) if asset_patterns else []

        # Build initial file mappings for closure files
        file_mappings: Dict[Path, Path] = {}
        for src in closure:
            try:
                rel = src.relative_to(staging_abs)
                outside = False
            except ValueError:
                rel = src
                outside = True

            # Determine default destination
            if (
                not outside
                and rel.name == binary.name
                and rel.parent.name == bin_dir.name
            ):
                dst = exe_out
            elif ".so" in src.name:  # Handles .so, .so.6, .so.6.7.0, etc.
                dst = out_root / lib_dir / src.name
            else:
                dst = out_root / rel if not outside else out_root / lib_dir / src.name

            file_mappings[src] = dst

        # Add asset files to mappings with a generic default location
        # Plugins will reorganize these through organize_files() if needed
        for f in asset_files:
            # By default, place asset files in lib directory
            # Plugins can override this in their organize_files method
            file_mappings[f] = out_root / lib_dir / f.name

        # Allow plugins to reorganize files
        for plugin in plugins:
            file_mappings = plugin.organize_files(file_mappings)

        # Copy all files to their destinations
        for src, dst in file_mappings.items():
            actions.copy_file(src, dst)
            if ".so" in dst.name or dst == exe_out:  # Handle versioned .so files
                actions.set_rpath_linux(dst, rpaths)

        # Ensure the main executable has correct rpaths
        if exe_out.exists() or not dry_run:
            actions.set_rpath_linux(exe_out, rpaths)

        for extra_lib_dir in [staging_abs / "lib", staging_abs / "usr/lib"]:
            if extra_lib_dir.exists():
                for f in sorted(extra_lib_dir.glob("*.so*")):
                    dst = out_root / lib_dir / f.name
                    actions.copy_file(f, dst)

                    actions.set_rpath_linux(dst, rpaths)

        # Process explicit copy mappings using base class method
        # Use project root as source since desktop files and icons are typically there
        self.process_copy_mappings(cfg, Path.cwd(), out_root, actions, default_dest="/")

        print(f"[linux] Bundled -> {out_root}")
        return 0

    def verify(self, cfg: Config) -> int:
        """Verify that all dependencies in the bundle are satisfied."""
        # Use correct config attribute access instead of .get()
        out_root = cfg.layout.linux.appdir
        targets: List[Path] = []

        # Check both usr/bin and usr/lib for binaries and libraries
        for rel in ("usr/bin", "usr/lib"):
            d = out_root / rel
            if d.exists():
                targets.extend(p for p in d.rglob("*") if p.is_file())

        # Use ldd to check each binary/library for missing dependencies
        for t in targets:
            r = run(["ldd", str(t)])
            if r.returncode != 0:
                continue
            for line in r.stdout.splitlines():
                if "not found" in line:
                    print(f"Missing dependency for {t}: {line}")
                    return 2
        return 0
