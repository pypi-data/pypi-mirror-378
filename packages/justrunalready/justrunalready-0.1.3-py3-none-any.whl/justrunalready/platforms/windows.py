from pathlib import Path

from justrunalready.config import Config
from justrunalready.utils import glob_many, Actions
from justrunalready.plugins.loader import load_plugins
from justrunalready.resolve import resolve_closure_windows


def bundle(
    cfg: Config,
    wrap: str | None = None,
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    staging = cfg.app.staging_root
    bin_dir = Path(cfg.layout.windows.bin_dir)
    exe_rel = Path(cfg.layout.windows.binary)
    if not (staging / exe_rel).exists():
        print(f"exe not found: {staging / exe_rel}")
        return 2
    actions = Actions(dry_run=dry_run, verbose=verbose)

    out_bin = staging / bin_dir
    actions.copy_file(staging / exe_rel, out_bin / exe_rel.name)

    plugins = list(load_plugins(cfg))
    seed_patterns = list(cfg.raw.get("include", []) or [])
    for plugin in plugins:
        seed_patterns.extend(list(plugin.seeds(stage_root=str(staging))))
    seed_files = glob_many(staging, seed_patterns)
    prunes: list[str] = []
    for plugin in plugins:
        if hasattr(plugin, "prune_patterns"):
            prunes.extend(list(plugin.prune_patterns()))
    closure = resolve_closure_windows(
        cfg, staging, exe_rel, seed_files, extra_excludes=prunes
    )

    plugin_dirs = [Path(p) for p in (cfg.layout.windows.plugin_dirs or [])]

    qt = None
    for p in plugins:
        if hasattr(p, "classify_plugin"):
            qt = p
            break

    for src in closure:
        try:
            rel = src.relative_to(staging)
        except Exception:
            continue
        preserve = False
        for pdir in plugin_dirs:
            try:
                rel.relative_to(pdir)
                preserve = True
                break
            except Exception:
                continue
        if preserve:
            dst = staging / rel
        elif qt is not None and getattr(qt, "classify_plugin")(src):
            cat = getattr(qt, "classify_plugin")(src)
            if plugin_dirs:
                dst = staging / plugin_dirs[0] / cat / src.name
            else:
                dst = out_bin / src.name
        elif src.suffix.lower() == ".dll":
            dst = out_bin / src.name
        else:
            dst = staging / rel
        actions.copy_file(src, dst)

    print(f"[windows] Bundled -> {out_bin}")
    return 0
