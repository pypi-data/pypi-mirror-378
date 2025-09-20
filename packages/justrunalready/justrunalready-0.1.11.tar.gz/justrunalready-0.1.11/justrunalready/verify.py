from __future__ import annotations

from pathlib import Path
from typing import List

from justrunalready.config import Config
from justrunalready.utils import run


def verify_linux(cfg: Config) -> int:
    out_root = Path(cfg.get("layout", "linux", "appdir", default="AppDir"))
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


def verify_windows(cfg: Config) -> int:
    staging = Path(cfg.get("app", "staging_root", default="install"))
    exe = staging / cfg.get("app", "binary", default="bin/app.exe")
    if not exe.exists():
        print(f"exe not found for verify: {exe}")
        return 2
    from justrunalready.inspectors.windows import list_needed

    imports = list_needed(exe)
    search_dirs = [exe.parent]
    for d in cfg.get("layout", "windows", "plugin_dirs", default=[]) or []:
        p = staging / d
        if p.exists():
            search_dirs.append(p)
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


def verify_macos(cfg: Config) -> int:
    app_path = Path(
        cfg.get("layout", "macos", "app_bundle", default="install/Index.app")
    )
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
