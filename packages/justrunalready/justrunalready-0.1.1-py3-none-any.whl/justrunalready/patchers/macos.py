from __future__ import annotations

from pathlib import Path

from justrunalready.utils import run


def have_install_name_tool() -> bool:
    r = run(["which", "install_name_tool"])
    return r.returncode == 0


def add_rpath(target: Path, rpath: str) -> bool:
    if not have_install_name_tool():
        return False
    r = run(["install_name_tool", "-add_rpath", rpath, str(target)])
    return r.returncode == 0


def set_id(target: Path, new_id: str) -> bool:
    if not have_install_name_tool():
        return False
    r = run(["install_name_tool", "-id", new_id, str(target)])
    return r.returncode == 0


def delete_rpath(target: Path, rpath: str) -> bool:
    if not have_install_name_tool():
        return False
    r = run(["install_name_tool", "-delete_rpath", rpath, str(target)])
    return r.returncode == 0


def list_rpaths(target: Path) -> list[str]:
    out = run(["otool", "-l", str(target)])
    if out.returncode != 0:
        return []
    rpaths: list[str] = []
    lines = out.stdout.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "cmd LC_RPATH":
            j = i + 1
            while j < len(lines) and "path" not in lines[j]:
                j += 1
            if j < len(lines):
                seg = lines[j].strip()
                import re

                m = re.match(r"path\s+(\S+)", seg)
                if m:
                    rpaths.append(m.group(1))
            i = j
        i += 1
    return rpaths
