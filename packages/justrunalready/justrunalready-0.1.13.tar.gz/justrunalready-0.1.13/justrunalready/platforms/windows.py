from pathlib import Path
from typing import Optional, Dict, List, Iterable, Set

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.utils.resolve import compile_patterns, is_excluded
from justrunalready.platforms.base import PlatformBase
from justrunalready.inspectors.loader import get_inspector


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

        exe_path = staging / bin_dir / binary
        if not exe_path.exists():
            print(f"exe not found: {exe_path}")
            return 2
        actions = Actions(dry_run=dry_run, verbose=verbose)

        out_bin = staging / bin_dir
        actions.copy_file(exe_path, out_bin / binary.name)

        seed_patterns = cfg.get_platform_includes("windows")
        seed_files = glob_many(staging, seed_patterns)

        closure = self.resolve_closure(cfg, staging / bin_dir / binary, seed_files)

        file_mappings: Dict[Path, Path] = {}
        for src in closure:
            try:
                rel = src.relative_to(staging)
            except ValueError:
                continue

            if src.suffix.lower() == ".dll":
                dst = out_bin / src.name
            else:
                dst = staging / rel

            file_mappings[src] = dst

        for src, dst in file_mappings.items():
            actions.copy_file(src, dst)

        self.process_copy_mappings(cfg, Path.cwd(), staging, actions, default_dest="/")

        print(f"[windows] Bundled -> {out_bin}")
        return 0

    def verify(self, cfg: Config) -> int:
        """Verify that all dependencies in the bundle are satisfied."""
        staging = cfg.app.staging_root
        bin_dir = Path(cfg.layout.windows.bin_dir)
        binary = Path(cfg.layout.windows.binary)
        exe = staging / bin_dir / binary

        if not exe.exists():
            print(f"exe not found for verify: {exe}")
            return 2

        inspector = get_inspector("windows")
        if not inspector:
            print("Windows inspector not available")
            return 2

        imports = inspector.list_needed(exe)

        search_dirs: List[Path] = [exe.parent]

        for name in imports:
            found = False
            for d in search_dirs:
                if (d / Path(name).name).exists():
                    found = True
                    break
            if not found:
                print(f"Missing DLL near exe: {name}")
                return 2
        return 0

    def resolve_closure(
        self,
        cfg: Config,
        exe_path: Path,
        seeds: Iterable[Path],
        extra_excludes: Optional[Iterable[str]] = None,
    ) -> Set[Path]:
        """Resolve the dependency closure for Windows."""
        inspector = get_inspector("windows")
        if not inspector:
            raise RuntimeError("Windows inspector not available")

        staging = cfg.app.staging_root
        search_dirs = self._get_search_dirs(staging, exe_path, cfg)
        work: List[Path] = [exe_path]
        seen: Set[Path] = set()
        for s in seeds:
            if s.exists():
                work.append(s)

        ex_list = cfg.get_platform_excludes("windows")
        if extra_excludes:
            ex_list = list(ex_list) + list(extra_excludes)
        ex_patterns = compile_patterns(ex_list)

        while work:
            cur = work.pop()
            try:
                cur = cur.resolve()
            except (OSError, RuntimeError):
                pass
            if cur in seen:
                continue
            seen.add(cur)

            if cur.suffix.lower() in (".exe", ".dll", ".pyd", ".sys"):
                for n in inspector.list_needed(cur):
                    resolved = self._resolve_needed(n, search_dirs)
                    if not resolved:
                        continue
                    if is_excluded(resolved, ex_patterns):
                        continue
                    if resolved not in seen:
                        work.append(resolved)

        return seen

    def _get_search_dirs(
        self, staging: Path, exe_path: Path, cfg: Config
    ) -> List[Path]:
        """Get DLL search directories for dependency resolution."""
        dirs: List[Path] = [exe_path.parent]
        for rel in ["bin", "lib"]:
            p = staging / rel
            if p.exists():
                dirs.append(p)
        return dirs

    def _resolve_needed(self, name: str, search_dirs: List[Path]) -> Optional[Path]:
        """Resolve a DLL dependency to a file path."""
        p = Path(name)
        if p.is_absolute() and p.exists():
            return p
        base = p.name
        for d in search_dirs:
            cand = d / base
            if cand.exists():
                return cand
        return None
