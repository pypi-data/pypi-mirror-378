from pathlib import Path
from typing import List, Optional, Dict, Iterable, Set
import re

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions, run
from justrunalready.utils.resolve import (
    compile_patterns,
    is_excluded,
    fetch_appimage_excludelist,
)
from justrunalready.platforms.base import PlatformBase
from justrunalready.inspectors.loader import get_inspector


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

        exe_path = staging_abs / bin_dir / binary
        if not exe_path.exists():
            print(f"binary not found: {exe_path}")
            return 2

        out_bin = out_root / bin_dir
        exe_out = out_bin / binary.name
        actions.copy_file(exe_path, exe_out)

        seed_patterns = cfg.get_platform_includes("linux")
        seed_files = glob_many(staging_abs, seed_patterns)

        closure = self.resolve_closure(cfg, staging_abs / bin_dir / binary, seed_files)

        file_mappings: Dict[Path, Path] = {}
        for src in closure:
            try:
                rel = src.relative_to(staging_abs)
                outside = False
            except ValueError:
                rel = src
                outside = True

            if (
                not outside
                and rel.name == binary.name
                and rel.parent.name == bin_dir.name
            ):
                dst = exe_out
            elif ".so" in src.name:
                dst = out_root / lib_dir / src.name
            else:
                dst = out_root / rel if not outside else out_root / lib_dir / src.name

            file_mappings[src] = dst

        for src, dst in file_mappings.items():
            actions.copy_file(src, dst)
            if ".so" in dst.name or dst == exe_out:
                actions.set_rpath_linux(dst, rpaths)

        if exe_out.exists() or not dry_run:
            actions.set_rpath_linux(exe_out, rpaths)

        for extra_lib_dir in [staging_abs / "lib", staging_abs / "usr/lib"]:
            if extra_lib_dir.exists():
                for f in sorted(extra_lib_dir.glob("*.so*")):
                    dst = out_root / lib_dir / f.name
                    actions.copy_file(f, dst)

                    actions.set_rpath_linux(dst, rpaths)

        self.process_copy_mappings(cfg, Path.cwd(), out_root, actions, default_dest="/")

        print(f"[linux] Bundled -> {out_root}")
        return 0

    def verify(self, cfg: Config) -> int:
        """Verify that all dependencies in the bundle are satisfied."""
        out_root = cfg.layout.linux.appdir
        targets: List[Path] = []

        for rel in ("usr/bin", "usr/lib"):
            d = out_root / rel
            if d.exists():
                targets.extend(p for p in d.rglob("*") if p.is_file())

        for t in targets:
            r = run(["ldd", str(t)])
            if r.returncode != 0:
                continue
            for line in r.stdout.splitlines():
                if "not found" in line:
                    print(f"Missing dependency for {t}: {line}")
                    return 2
        return 0

    def resolve_closure(
        self,
        cfg: Config,
        exe_path: Path,
        seeds: Iterable[Path],
        extra_excludes: Optional[Iterable[str]] = None,
    ) -> Set[Path]:
        """Resolve the dependency closure for Linux."""
        inspector = get_inspector("linux")
        if not inspector:
            raise RuntimeError("Linux inspector not available")

        staging = cfg.app.staging_root
        search_dirs = self._get_search_dirs(staging, exe_path, cfg)
        work: List[Path] = [exe_path]
        seen: Set[Path] = set()
        for s in seeds:
            if s.exists():
                work.append(s)

        ex_list = cfg.get_platform_excludes("linux")
        if extra_excludes:
            ex_list = list(ex_list) + list(extra_excludes)
        ex_patterns = compile_patterns(ex_list)

        include_list = []

        appimage_excludes = fetch_appimage_excludelist()

        while work:
            cur = work.pop()
            try:
                cur = cur.resolve()
            except (OSError, RuntimeError):
                pass
            if cur in seen:
                continue
            seen.add(cur)

            needs = inspector.list_needed(cur)
            for n in needs:
                resolved = self._resolve_needed(n, search_dirs) or self._resolve_needed(
                    n, self._get_system_dirs()
                )
                if not resolved:
                    continue

                if is_excluded(resolved, ex_patterns):
                    continue

                lib_name = resolved.name
                if lib_name in appimage_excludes:
                    explicitly_included = False
                    for inc in include_list:
                        if inc in lib_name or lib_name == inc:
                            explicitly_included = True
                            break
                    if not explicitly_included:
                        continue

                if resolved not in seen:
                    work.append(resolved)

        return seen

    def _read_rpaths(self, elf: Path) -> List[str]:
        """Read RPATH/RUNPATH from an ELF binary."""
        r = run(["which", "patchelf"])
        if r.returncode == 0:
            pr = run(["patchelf", "--print-rpath", str(elf)])
            if pr.returncode == 0:
                s = (pr.stdout or "").strip()
                return [p for p in s.split(":") if p]

        if run(["which", "readelf"]).returncode == 0:
            out = run(["readelf", "-d", str(elf)])
            if out.returncode == 0:
                rpaths: List[str] = []
                for line in out.stdout.splitlines():
                    m = re.search(r"R(PATH|UNPATH).*\[(.*?)\]", line)
                    if m:
                        rpaths.extend([p for p in m.group(2).split(":") if p])
                return rpaths
        return []

    def _expand_origin(self, rpaths: Iterable[str], base: Path) -> List[str]:
        """Expand $ORIGIN in RPATH entries."""
        out: List[str] = []
        for p in rpaths:
            out.append(p.replace("$ORIGIN", str(base)))
        return out

    def _get_system_dirs(self) -> List[Path]:
        """Get standard system library directories."""
        return [Path("/lib"), Path("/lib64"), Path("/usr/lib"), Path("/usr/lib64")]

    def _get_search_dirs(self, staging: Path, exe: Path, cfg: Config) -> List[Path]:
        """Get library search directories for dependency resolution."""
        dirs: List[Path] = []
        rpaths = self._read_rpaths(exe)
        dirs.extend(Path(p) for p in self._expand_origin(rpaths, exe.parent))
        for c in [
            staging / "lib",
            staging / "usr/lib",
            staging / "lib64",
            staging / "usr/lib64",
            staging / "bin",
        ]:
            if c.exists():
                dirs.append(c)
        return dirs

    def _resolve_needed(
        self, name_or_path: str, search_dirs: List[Path]
    ) -> Optional[Path]:
        """Resolve a library dependency to a file path."""
        p = Path(name_or_path)
        if p.is_absolute() and p.exists():
            return p
        for d in search_dirs:
            candidate = d / name_or_path
            if candidate.exists():
                return candidate
        base = Path(name_or_path).name
        for d in search_dirs:
            cand = d / base
            if cand.exists():
                return cand
        return None
