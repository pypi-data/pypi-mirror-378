import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Iterable, Set

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions, run
from justrunalready.utils.resolve import compile_patterns, is_excluded
from justrunalready.platforms.base import PlatformBase
from justrunalready.inspectors.loader import get_inspector


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
        frameworks_dir = app_path / cfg.layout.macos.lib_dir
        rpaths: List[str] = cfg.layout.macos.rpath or []
        actions = Actions(dry_run=dry_run, verbose=verbose)

        if not app_path.exists():
            print(f"app_bundle not found: {app_path}")
            return 2

        staging_root = cfg.app.staging_root

        seed_patterns = cfg.get_platform_includes("macos")
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

        closure = self.resolve_closure(cfg, exe_path, seed_files)

        file_mappings: Dict[Path, Path] = {}
        changes: dict[str, str] = {}

        for src in closure:
            try:
                rel = src.relative_to(app_path)
                dst = app_path / rel
            except ValueError:
                if ".dylib" in src.name or ".framework" in src.name:
                    dst = frameworks_dir / src.name
                    changes[str(src)] = f"@rpath/{dst.name}"
                else:
                    dst = frameworks_dir / src.name

            file_mappings[src] = dst

        for src, dst in file_mappings.items():
            if not src.exists():
                continue
            actions.copy_file(src, dst)

            if ".dylib" in dst.name or ".framework" in dst.name:
                if str(src) in changes:
                    actions.set_id_macos(dst, changes[str(src)])

            if (
                ".dylib" in dst.name
                or ".framework" in dst.name
                or dst.suffix == ""
                or dst == exe_path
            ):
                actions.set_exact_rpaths_macos(dst, rpaths)

        inspector = get_inspector("macos")
        if not inspector:
            print("Warning: macOS inspector not available")
            inspector = None

        for src, dst in file_mappings.items():
            try:
                src.relative_to(app_path)
                p = src
            except ValueError:
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
                dst = frameworks_dir / f.name
                actions.copy_file(f, dst)
                actions.set_id_macos(dst, f"@rpath/{dst.name}")
                actions.set_exact_rpaths_macos(dst, rpaths)

        self.process_copy_mappings(
            cfg, Path.cwd(), app_path, actions, default_dest="Contents/Resources"
        )

        print(f"[macOS] Bundled -> {app_path}")
        return 0

    def verify(self, cfg: Config) -> int:
        """Verify that all dependencies in the bundle are satisfied."""
        app_path = cfg.layout.macos.app_bundle

        if not app_path.exists():
            print(f"App bundle not found: {app_path}")
            return 2

        for rel in ("Contents/MacOS", "Contents/Frameworks"):
            d = app_path / rel
            if not d.exists():
                continue
            for t in d.rglob("*"):
                if not t.is_file():
                    continue
                r = run(["otool", "-L", str(t)])
                if r.returncode != 0:
                    continue
                for line in r.stdout.splitlines()[1:]:
                    dep = line.strip().split(" ")[0]
                    if dep.startswith("/System/") or dep.startswith("/usr/lib/"):
                        continue
                    if (
                        dep.startswith("@rpath")
                        or dep.startswith("@executable_path")
                        or dep.startswith("@loader_path")
                    ):
                        continue
                    print(f"Suspicious absolute dependency in {t}: {dep}")
                    return 2
        return 0

    def resolve_closure(
        self,
        cfg: Config,
        exe_path: Path,
        seeds: Iterable[Path],
        extra_excludes: Optional[Iterable[str]] = None,
    ) -> Set[Path]:
        """Resolve the dependency closure for macOS."""
        inspector = get_inspector("macos")
        if not inspector:
            raise RuntimeError("macOS inspector not available")

        app_root = cfg.layout.macos.app_bundle
        search_dirs = self._get_search_dirs(app_root, exe_path)
        work: List[Path] = [exe_path]
        seen: Set[Path] = set()
        for s in seeds:
            if s.exists():
                work.append(s)

        ex_list = cfg.get_platform_excludes("macos")
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

            for n in inspector.list_needed(cur):
                resolved = self._resolve_needed(n, app_root, cur, search_dirs)
                if not resolved:
                    continue
                if is_excluded(resolved, ex_patterns):
                    continue
                if resolved not in seen:
                    work.append(resolved)

        return seen

    def _read_rpaths(self, macho: Path) -> List[str]:
        """Read RPATH entries from a Mach-O binary."""
        out = run(["otool", "-l", str(macho)])
        if out.returncode != 0:
            return []
        rpaths: List[str] = []
        lines = out.stdout.splitlines()
        i = 0
        while i < len(lines):
            if lines[i].strip() == "cmd LC_RPATH":
                j = i + 1
                while j < len(lines) and "path" not in lines[j]:
                    j += 1
                if j < len(lines):
                    seg = lines[j].strip()
                    m = re.match(r"path\s+(\S+)", seg)
                    if m:
                        rpaths.append(m.group(1))
                i = j
            i += 1
        return rpaths

    def _expand_token(self, s: str, base: Path, loader: Path) -> str:
        """Expand @executable_path and @loader_path tokens."""
        s = s.replace("@executable_path", str(base))
        s = s.replace("@loader_path", str(loader.parent))
        return s

    def _get_search_dirs(self, app_root: Path, macho: Path) -> List[Path]:
        """Get library search directories for dependency resolution."""
        base = app_root / "Contents" / "MacOS"
        dirs: List[Path] = [base]
        for rp in self._read_rpaths(macho):
            rp = self._expand_token(rp, base, macho)
            p = Path(rp)
            if not p.is_absolute():
                p = (macho.parent / rp).resolve()
            dirs.append(p)
        dirs.append(app_root / "Contents" / "Frameworks")
        dirs.append(app_root / "Contents" / "PlugIns")
        return dirs

    def _resolve_needed(
        self, spec: str, app_root: Path, macho: Path, search_dirs: List[Path]
    ) -> Optional[Path]:
        """Resolve a library dependency to a file path."""
        if spec.startswith("@rpath"):
            for d in search_dirs:
                if not d.is_absolute():
                    continue
                cand = d / spec.replace("@rpath/", "")
                if cand.exists():
                    return cand
            return None
        if spec.startswith("@executable_path") or spec.startswith("@loader_path"):
            base = app_root / "Contents" / "MacOS"
            path = Path(self._expand_token(spec, base, macho))
            if not path.is_absolute():
                path = (macho.parent / path).resolve()
            return path if path.exists() else None
        p = Path(spec)
        if p.is_absolute() and p.exists():
            return p
        base = p.name
        for d in search_dirs:
            cand = d / base
            if cand.exists():
                return cand
        return None
