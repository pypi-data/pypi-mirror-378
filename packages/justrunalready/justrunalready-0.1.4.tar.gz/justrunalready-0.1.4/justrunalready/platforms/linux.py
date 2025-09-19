from pathlib import Path
from typing import List

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.plugins.loader import load_plugins
from justrunalready.resolve import resolve_closure_linux


def bundle(
    cfg: Config,
    wrap: str | None = None,
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
    app_rel = Path(cfg.layout.linux.binary)
    actions = Actions(dry_run=dry_run, verbose=verbose)

    if not (staging_abs / app_rel).exists():
        print(f"binary not found: {staging_abs / app_rel}")
        return 2

    out_bin = out_root / bin_dir
    exe_out = out_bin / app_rel.name
    actions.copy_file(staging_abs / app_rel, exe_out)

    plugins = list(load_plugins(cfg))
    seed_patterns = cfg.get_platform_includes("linux")
    for plugin in plugins:
        seed_patterns.extend(list(plugin.seeds(stage_root=str(staging_abs))))
    seed_files = glob_many(staging_abs, seed_patterns)
    prunes: List[str] = []
    for plugin in plugins:
        if hasattr(plugin, "prune_patterns"):
            prunes.extend(list(plugin.prune_patterns()))
    closure = resolve_closure_linux(
        cfg, staging, app_rel, seed_files, extra_excludes=prunes
    )

    asset_patterns: List[str] = []
    for plugin in plugins:
        if hasattr(plugin, "asset_seeds"):
            asset_patterns.extend(list(plugin.asset_seeds(stage_root=str(staging_abs))))
    asset_files = glob_many(Path("/"), asset_patterns) if asset_patterns else []
    qml_dir = Path(cfg.layout.linux.qml_dir)

    qml_roots: List[Path] = []
    for plugin in plugins:
        if hasattr(plugin, "qml_roots"):
            qml_roots.extend(list(plugin.qml_roots(str(staging_abs))))
    for f in asset_files:
        dest = None
        for r in qml_roots:
            try:
                rel = f.relative_to(r)
                dest = out_root / qml_dir / rel
                break
            except ValueError:
                continue
        if dest is None:
            continue
        actions.copy_file(f, dest)

    plugin_dirs = [Path(p) for p in (cfg.layout.linux.plugin_dirs or [])]

    qt = None
    for p in plugins:
        if hasattr(p, "classify_plugin"):
            qt = p
            break

    for src in closure:
        try:
            rel = src.relative_to(staging_abs)
            outside = False
        except ValueError:
            rel = src
            outside = True

        preserve = False
        for pdir in plugin_dirs:
            try:
                rel.relative_to(pdir)
                preserve = True
                break
            except ValueError:
                continue

        if preserve and not outside:
            dst = out_root / rel
        else:
            cat = None
            if qt is not None:
                cat = qt.classify_plugin(src)
            if cat and plugin_dirs:
                dst = out_root / plugin_dirs[0] / cat / src.name

            elif (
                not outside
                and rel.name == app_rel.name
                and rel.parent.name == app_rel.parent.name
            ):
                dst = exe_out
            elif src.suffix == ".so":
                dst = out_root / lib_dir / src.name
            else:
                dst = out_root / rel if not outside else out_root / lib_dir / src.name

        actions.copy_file(src, dst)
        if dst.suffix == ".so" or dst == exe_out:
            actions.set_rpath_linux(dst, rpaths)

    actions.copy_file(staging_abs / app_rel, exe_out)
    actions.set_rpath_linux(exe_out, rpaths)

    for extra_lib_dir in [staging_abs / "lib", staging_abs / "usr/lib"]:
        if extra_lib_dir.exists():
            for f in sorted(extra_lib_dir.glob("*.so*")):
                dst = out_root / lib_dir / f.name
                actions.copy_file(f, dst)

                actions.set_rpath_linux(dst, rpaths)

    print(f"[linux] Bundled -> {out_root}")
    return 0
