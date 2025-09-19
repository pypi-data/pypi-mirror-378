import os
from pathlib import Path
from typing import List

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.plugins.loader import load_plugins
from justrunalready.resolve import resolve_closure_macos
from justrunalready.inspectors.macos import list_needed


def bundle(
    cfg: Config,
    wrap: str | None = None,
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

    plugins = list(load_plugins(cfg))
    staging_root = cfg.app.staging_root
    seed_patterns = list(cfg.raw.get("include", []) or [])
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
    exe_rel = Path("Contents/MacOS") / exe_name

    prunes: List[str] = []
    for plugin in plugins:
        if hasattr(plugin, "prune_patterns"):
            prunes.extend(list(plugin.prune_patterns()))
    closure = resolve_closure_macos(
        cfg, app_path, exe_rel, seed_files, extra_excludes=prunes
    )

    asset_patterns: List[str] = []
    for plugin in plugins:
        if hasattr(plugin, "asset_seeds"):
            asset_patterns.extend(
                list(plugin.asset_seeds(stage_root=str(staging_root)))
            )
    asset_files = glob_many(Path("/"), asset_patterns) if asset_patterns else []
    qml_dir = Path(cfg.layout.macos.qml_dir)
    qml_roots: List[Path] = []
    for plugin in plugins:
        if hasattr(plugin, "qml_roots"):
            qml_roots.extend(list(plugin.qml_roots(str(staging_root))))
    for f in asset_files:
        dest = None
        for r in qml_roots:
            try:
                rel = f.relative_to(r)
                dest = app_path / qml_dir / rel
                break
            except Exception:
                continue
        if dest is None:
            continue
        actions.copy_file(f, dest)

    changes: dict[str, str] = {}

    qt = None
    for p in plugins:
        if hasattr(p, "classify_plugin"):
            qt = p
            break

    for src in closure:
        try:
            rel = src.relative_to(app_path)
            dst = app_path / rel
        except Exception:
            cat = None
            if qt is not None:
                try:
                    cat = qt.classify_plugin(src)
                except Exception:
                    cat = None
            if cat:
                dst = app_path / plugins_dir / cat / src.name
                actions.copy_file(src, dst)
            elif src.suffix == ".dylib" or ".framework" in src.name:
                dst = app_path / frameworks_dir / src.name
                actions.copy_file(src, dst)
                actions.set_id_macos(dst, f"@rpath/{dst.name}")
                changes[str(src)] = f"@rpath/{dst.name}"
            else:
                dst = app_path / plugins_dir / src.name
                actions.copy_file(src, dst)
        actions.set_exact_rpaths_macos(dst, rpaths)

    for p in closure:
        try:
            p.relative_to(app_path)
        except Exception:
            continue

        for dep in list_needed(p):
            dep_path = Path(dep)
            if str(dep_path).startswith(str(app_path / "Contents/Frameworks")):
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

    print(f"[macOS] Bundled -> {app_path}")
    return 0
