from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from typing import Iterable, List, Optional, Set

from justrunalready.config import Config
from justrunalready.utils import run


def _compile_patterns(patterns: Iterable[str]) -> List[re.Pattern[str]]:
    return [re.compile(p) for p in patterns]


def _is_excluded(path: Path, patterns: List[re.Pattern[str]]) -> bool:
    sp = path.as_posix()
    return any(p.search(sp) for p in patterns)


def _linux_read_rpaths(elf: Path) -> List[str]:
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


def _expand_origin(rpaths: Iterable[str], base: Path) -> List[str]:
    out: List[str] = []
    for p in rpaths:
        out.append(p.replace("$ORIGIN", str(base)))
    return out


def _linux_system_dirs() -> List[Path]:
    return [Path("/lib"), Path("/lib64"), Path("/usr/lib"), Path("/usr/lib64")]


def _fetch_appimage_excludelist() -> List[str]:
    """Fetch the AppImage excludelist from GitHub."""
    try:
        url = "https://raw.githubusercontent.com/probonopd/AppImages/master/excludelist"
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
            excludes = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    excludes.append(line)
            return excludes
    except Exception as e:
        print(f"Warning: Could not fetch AppImage excludelist: {e}")
        # If fetch fails, use a minimal fallback list
        return [
            "ld-linux.so.2",
            "ld-linux-x86-64.so.2",
            "libc.so.6",
            "libm.so.6",
            "libdl.so.2",
            "libpthread.so.0",
            "librt.so.1",
            "libresolv.so.2",
        ]


def _linux_search_dirs(staging: Path, exe: Path, cfg: Config) -> List[Path]:
    dirs: List[Path] = []
    rpaths = _linux_read_rpaths(exe)
    dirs.extend(Path(p) for p in _expand_origin(rpaths, exe.parent))
    for c in [
        staging / "lib",
        staging / "usr/lib",
        staging / "lib64",
        staging / "usr/lib64",
        staging / "bin",
    ]:
        if c.exists():
            dirs.append(c)
    for d in cfg.get("layout", "linux", "plugin_dirs", default=[]) or []:
        p = staging / d
        if p.exists():
            dirs.append(p)
    return dirs


def _linux_resolve_needed(name_or_path: str, search_dirs: List[Path]) -> Optional[Path]:
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


def resolve_closure_linux(
    cfg: Config,
    staging: Path,
    exe_rel: Path,
    seeds: Iterable[Path],
    extra_excludes: Optional[Iterable[str]] = None,
) -> Set[Path]:
    from justrunalready.inspectors import get_inspector

    inspector = get_inspector("linux")
    if not inspector:
        raise RuntimeError("Linux inspector not available")

    exe_path = staging / exe_rel
    search_dirs = _linux_search_dirs(staging, exe_path, cfg)
    work: List[Path] = [exe_path]
    seen: Set[Path] = set()
    for s in seeds:
        if s.exists():
            work.append(s)

    # Get user-specified exclusions and includes
    ex_list = cfg.get("exclude", default=[]) or []
    if extra_excludes:
        ex_list = list(ex_list) + list(extra_excludes)
    ex_patterns = _compile_patterns(ex_list)

    # Get explicit includes from config (if any)
    include_list = cfg.get("include_system_libs", default=[]) or []

    # Fetch AppImage excludelist
    appimage_excludes = _fetch_appimage_excludelist()

    while work:
        cur = work.pop()
        try:
            cur = cur.resolve()
        except (OSError, RuntimeError):
            # Skip broken symlinks or inaccessible paths
            pass
        if cur in seen:
            continue
        seen.add(cur)

        needs = inspector.list_needed(cur)
        for n in needs:
            resolved = _linux_resolve_needed(n, search_dirs) or _linux_resolve_needed(
                n, _linux_system_dirs()
            )
            if not resolved:
                continue

            # Check if user explicitly excluded this
            if _is_excluded(resolved, ex_patterns):
                continue

            # Check AppImage excludelist, but allow explicit includes to override
            lib_name = resolved.name
            if lib_name in appimage_excludes:
                # Check if user explicitly included this library
                explicitly_included = False
                for inc in include_list:
                    if inc in lib_name or lib_name == inc:
                        explicitly_included = True
                        break
                if not explicitly_included:
                    # Skip this system library
                    continue

            if resolved not in seen:
                work.append(resolved)

    return seen


def _macos_read_rpaths(macho: Path) -> List[str]:
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


def _macos_expand_token(s: str, base: Path, loader: Path) -> str:
    s = s.replace("@executable_path", str(base))
    s = s.replace("@loader_path", str(loader.parent))
    return s


def _macos_search_dirs(app_root: Path, macho: Path) -> List[Path]:
    base = app_root / "Contents" / "MacOS"
    dirs: List[Path] = [base]
    for rp in _macos_read_rpaths(macho):
        rp = _macos_expand_token(rp, base, macho)
        p = Path(rp)
        if not p.is_absolute():
            p = (macho.parent / rp).resolve()
        dirs.append(p)
    dirs.append(app_root / "Contents" / "Frameworks")
    dirs.append(app_root / "Contents" / "PlugIns")
    return dirs


def _macos_resolve_needed(
    spec: str, app_root: Path, macho: Path, search_dirs: List[Path]
) -> Optional[Path]:
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
        path = Path(_macos_expand_token(spec, base, macho))
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


def resolve_closure_macos(
    cfg: Config,
    app_root: Path,
    exe_rel: Path,
    seeds: Iterable[Path],
    extra_excludes: Optional[Iterable[str]] = None,
) -> Set[Path]:
    from justrunalready.inspectors import get_inspector

    inspector = get_inspector("macos")
    if not inspector:
        raise RuntimeError("macOS inspector not available")

    exe_path = app_root / exe_rel
    search_dirs = _macos_search_dirs(app_root, exe_path)
    work: List[Path] = [exe_path]
    seen: Set[Path] = set()
    for s in seeds:
        if s.exists():
            work.append(s)

    ex_list = cfg.get("exclude", default=[]) or []
    if extra_excludes:
        ex_list = list(ex_list) + list(extra_excludes)
    ex_patterns = _compile_patterns(ex_list)

    while work:
        cur = work.pop()
        try:
            cur = cur.resolve()
        except (OSError, RuntimeError):
            # Skip broken symlinks or inaccessible paths
            pass
        if cur in seen:
            continue
        seen.add(cur)

        for n in inspector.list_needed(cur):
            resolved = _macos_resolve_needed(n, app_root, cur, search_dirs)
            if not resolved:
                continue
            if _is_excluded(resolved, ex_patterns):
                continue
            if resolved not in seen:
                work.append(resolved)

    return seen


def _windows_search_dirs(staging: Path, exe_path: Path, cfg: Config) -> List[Path]:
    dirs: List[Path] = [exe_path.parent]
    for rel in ["bin", "lib"]:
        p = staging / rel
        if p.exists():
            dirs.append(p)
    for d in cfg.get("layout", "windows", "plugin_dirs", default=[]) or []:
        p = staging / d
        if p.exists():
            dirs.append(p)
    return dirs


def _windows_resolve_needed(name: str, search_dirs: List[Path]) -> Optional[Path]:
    p = Path(name)
    if p.is_absolute() and p.exists():
        return p
    base = p.name
    for d in search_dirs:
        cand = d / base
        if cand.exists():
            return cand
    return None


def resolve_closure_windows(
    cfg: Config,
    staging: Path,
    exe_rel: Path,
    seeds: Iterable[Path],
    extra_excludes: Optional[Iterable[str]] = None,
) -> Set[Path]:
    from justrunalready.inspectors import get_inspector

    inspector = get_inspector("windows")
    if not inspector:
        raise RuntimeError("Windows inspector not available")

    exe_path = staging / exe_rel
    search_dirs = _windows_search_dirs(staging, exe_path, cfg)
    work: List[Path] = [exe_path]
    seen: Set[Path] = set()
    for s in seeds:
        if s.exists():
            work.append(s)

    ex_list = cfg.get("exclude", default=[]) or []
    if extra_excludes:
        ex_list = list(ex_list) + list(extra_excludes)
    ex_patterns = _compile_patterns(ex_list)

    while work:
        cur = work.pop()
        try:
            cur = cur.resolve()
        except (OSError, RuntimeError):
            # Skip broken symlinks or inaccessible paths
            pass
        if cur in seen:
            continue
        seen.add(cur)

        # Only try to parse PE files (executables and DLLs)
        if cur.suffix.lower() in ('.exe', '.dll', '.pyd', '.sys'):
            for n in inspector.list_needed(cur):
                resolved = _windows_resolve_needed(n, search_dirs)
                if not resolved:
                    continue
                if _is_excluded(resolved, ex_patterns):
                    continue
                if resolved not in seen:
                    work.append(resolved)

    return seen
