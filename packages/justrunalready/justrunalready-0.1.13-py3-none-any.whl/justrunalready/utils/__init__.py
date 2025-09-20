"""Shared utilities for justrunalready."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


def run(
    cmd: Sequence[str], cwd: Optional[Path] = None, timeout: Optional[float] = 300
) -> subprocess.CompletedProcess:
    """Run a subprocess command.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory for the command
        timeout: Maximum time in seconds to wait (default: 300s/5min)

    Returns:
        CompletedProcess result

    Raises:
        subprocess.TimeoutExpired: If the command times out
    """
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def glob_many(root: Path, patterns: Iterable[str]) -> List[Path]:
    """Glob multiple patterns and return matching paths.

    Patterns starting with '!' are exclusion patterns that remove previously matched files.
    """
    included: set[Path] = set()
    excluded: set[Path] = set()
    import glob as _glob

    for pat in patterns:
        if pat.startswith("!"):
            exclude_pat = pat[1:]
            p = Path(exclude_pat)
            if p.is_absolute():
                excluded.update(
                    Path(x) for x in _glob.glob(exclude_pat, recursive=True)
                )
            else:
                excluded.update(root.glob(exclude_pat))
        else:
            p = Path(pat)
            if p.is_absolute():
                included.update(Path(x) for x in _glob.glob(pat, recursive=True))
            else:
                included.update(root.glob(pat))

    return list(included - excluded)


class Actions:
    """Helper to perform or only log actions when in dry-run mode."""

    def __init__(self, *, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose

    def log(self, msg: str) -> None:
        if self.dry_run or self.verbose:
            print(("DRYRUN: " if self.dry_run else "") + msg)

    def copy_file(self, src: Path, dst: Path) -> None:
        if self.dry_run:
            self.log(f"COPY {src} -> {dst}")
            return
        ensure_dir(dst.parent)
        shutil.copy2(src, dst)
        self.log(f"COPY {src} -> {dst}")

    def set_rpath_linux(self, target: Path, rpaths: List[str]) -> bool:
        from justrunalready.patchers.linux import set_rpath

        if self.dry_run:
            self.log(f"SETRPATH {target} [{':'.join(rpaths)}]")
            return True
        ok = set_rpath(target, rpaths)
        self.log(f"SETRPATH {target} [{':'.join(rpaths)}] -> {'ok' if ok else 'fail'}")
        return ok

    def add_rpath_macos(self, target: Path, rpath: str) -> bool:
        from justrunalready.patchers.macos import add_rpath

        if self.dry_run:
            self.log(f"ADDRPATH {target} {rpath}")
            return True
        ok = add_rpath(target, rpath)
        self.log(f"ADDRPATH {target} {rpath} -> {'ok' if ok else 'fail'}")
        return ok

    def set_id_macos(self, target: Path, new_id: str) -> bool:
        from justrunalready.patchers.macos import set_id

        if self.dry_run:
            self.log(f"SETID {target} {new_id}")
            return True
        ok = set_id(target, new_id)
        self.log(f"SETID {target} {new_id} -> {'ok' if ok else 'fail'}")
        return ok

    def change_install_name_macos(self, file: Path, old: str, new: str) -> None:
        import subprocess

        if self.dry_run:
            self.log(f"CHANGEID {file} {old} -> {new}")
            return
        subprocess.run(
            ["install_name_tool", "-change", old, new, str(file)], capture_output=True
        )
        self.log(f"CHANGEID {file} {old} -> {new}")

    def set_exact_rpaths_macos(self, file: Path, desired: list[str]) -> None:
        from justrunalready.patchers.macos import list_rpaths, delete_rpath

        current = set(list_rpaths(file))
        want = set(desired)
        for rp in sorted(current - want):
            if self.dry_run:
                self.log(f"DELRPATH {file} {rp}")
            else:
                delete_rpath(file, rp)
        for rp in sorted(want - current):
            self.add_rpath_macos(file, rp)
