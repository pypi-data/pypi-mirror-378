from __future__ import annotations

from pathlib import Path

from justrunalready.utils import run


def have_patchelf() -> bool:
    r = run(["which", "patchelf"])
    return r.returncode == 0


def set_rpath(target: Path, rpaths: list[str]) -> bool:
    if not have_patchelf():
        return False
    r = run(["patchelf", "--set-rpath", ":".join(rpaths), str(target)])
    return r.returncode == 0
