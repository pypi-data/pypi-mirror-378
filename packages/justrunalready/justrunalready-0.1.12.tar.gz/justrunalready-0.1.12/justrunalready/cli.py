from __future__ import annotations

import argparse
import sys
from pathlib import Path

from justrunalready.config import load_config
from justrunalready.wrappers.loader import load_wrappers


def _cmd_bundle(args: argparse.Namespace) -> int:
    from justrunalready.platforms.loader import get_platform

    cfg = load_config(Path(args.config))
    platform_name = _normalize_platform(getattr(args, "platform", "auto"))

    # Normalize platform names
    if platform_name.startswith("linux"):
        platform_name = "linux"
    elif platform_name in ("macos", "darwin"):
        platform_name = "macos"
    elif platform_name.startswith("win") or platform_name == "windows":
        platform_name = "windows"

    platform = get_platform(platform_name)
    if platform is None:
        print(f"Unsupported platform: {platform_name}", file=sys.stderr)
        return 2

    rc = platform.bundle(
        cfg,
        wrap=args.wrap,
        dry_run=args.dry_run,
        verbose=getattr(args, "verbose", False),
    )

    if rc == 0 and args.wrap:
        _run_wrapper(args.wrap, cfg, platform_name)

    return rc


def _cmd_scan(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))

    from .scan import print_dependency_graph

    return print_dependency_graph(cfg)


def _cmd_clean(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    cache = cwd / ".jra"
    if cache.exists():
        for p in sorted(cache.rglob("*"), reverse=True):
            try:
                if p.is_file() or p.is_symlink():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    p.rmdir()
            except (OSError, PermissionError):
                # Best effort cleanup - ignore if we can't delete
                pass
        try:
            cache.rmdir()
        except (OSError, PermissionError):
            # Best effort cleanup - ignore if we can't delete
            pass
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    from justrunalready.platforms.loader import get_platform

    cfg = load_config(Path(args.config))
    platform_name = _normalize_platform(getattr(args, "platform", "auto"))

    # Normalize platform names (same logic as _cmd_bundle)
    if platform_name.startswith("linux"):
        platform_name = "linux"
    elif platform_name in ("macos", "darwin"):
        platform_name = "macos"
    elif platform_name.startswith("win") or platform_name == "windows":
        platform_name = "windows"

    platform = get_platform(platform_name)
    if platform is None:
        print(f"Unsupported platform: {platform_name}", file=sys.stderr)
        return 2

    # Call the verify method on the platform instance
    return platform.verify(cfg)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jra", description="JustRunAlready bundler")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_bundle = sub.add_parser("bundle", help="Bundle app into platform layout")
    p_bundle.add_argument("--config", required=True, help="Path to jra.toml config")
    p_bundle.add_argument(
        "--platform", default=None, help="Override platform autodetect"
    )
    p_bundle.add_argument(
        "--wrap",
        default=None,
        choices=["appimage", "dmg", "zip"],
        help="Optionally wrap output",
    )
    p_bundle.add_argument(
        "--dry-run", action="store_true", help="Plan only; do not modify files"
    )
    p_bundle.add_argument(
        "--verbose", action="store_true", help="Print operations while bundling"
    )
    p_bundle.set_defaults(func=_cmd_bundle)

    p_scan = sub.add_parser("scan", help="Print dependency graph")
    p_scan.add_argument("--config", required=True, help="Path to jra.toml config")
    p_scan.set_defaults(func=_cmd_scan)

    p_clean = sub.add_parser("clean", help="Remove JRA cache/state")
    p_clean.set_defaults(func=_cmd_clean)

    p_verify = sub.add_parser(
        "verify", help="Verify bundled dependencies are self-contained"
    )
    p_verify.add_argument("--config", required=True, help="Path to jra.toml config")
    p_verify.add_argument(
        "--platform", default=None, help="Override platform autodetect"
    )
    p_verify.set_defaults(func=_cmd_verify)

    p_info = sub.add_parser("info", help="Print resolved bundle and artifact info")
    p_info.add_argument("--config", required=True, help="Path to jra.toml config")
    p_info.add_argument(
        "--platform", default="auto", help="Platform: auto|linux|macos|windows"
    )
    p_info.add_argument("--wrap", default="", help="Optional wrapper: appimage|dmg|zip")
    p_info.add_argument(
        "--format", default="env", choices=["env", "json"], help="Output format"
    )
    p_info.set_defaults(func=_cmd_info)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


def _normalize_platform(p: str) -> str:
    p = (p or "auto").lower()
    if p == "auto":
        import sys as _sys

        if _sys.platform.startswith("linux"):
            return "linux"
        if _sys.platform == "darwin":
            return "macos"
        if _sys.platform.startswith("win"):
            return "windows"
        return _sys.platform
    if p in ("darwin", "mac"):
        return "macos"
    if p.startswith("win"):
        return "windows"
    return p


def _cmd_info(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))
    plat = _normalize_platform(args.platform)

    name = cfg.app.name
    bundle_path = ""
    if plat == "linux":
        bundle_path = str(cfg.layout.linux.appdir)
    elif plat == "macos":
        bundle_path = str(cfg.layout.macos.app_bundle)
    elif plat == "windows":
        bundle_path = str(Path("install") / cfg.layout.windows.bin_dir)

    artifact_path = ""
    wrap = (args.wrap or "").strip().lower()
    if wrap:
        if wrap == "appimage":
            artifact_path = f"{name}-linux-x86_64.AppImage"
        elif wrap == "dmg":
            artifact_path = f"{name}-macos.dmg"
        elif wrap == "zip":
            artifact_path = f"{name}.zip"

    if args.format == "json":
        import json as _json

        print(
            _json.dumps(
                {
                    "name": name,
                    "platform": plat,
                    "bundle_path": bundle_path,
                    "artifact_path": artifact_path,
                }
            )
        )
    else:
        # env format for easy piping to $GITHUB_OUTPUT
        print(f"name={name}")
        print(f"platform={plat}")
        print(f"bundle_path={bundle_path}")
        print(f"artifact_path={artifact_path}")
    return 0


def _run_wrapper(name: str, cfg, platform: str) -> None:
    wrappers = load_wrappers()
    w = wrappers.get(name)
    if not w:
        print(f"Wrapper not found: {name}")
        return
    if not w.supports(platform):
        print(f"Wrapper {name} does not support platform {platform}")
        return
    try:
        out = w.run(cfg)
        print(f"Wrapped artifact: {out}")
    except Exception as e:
        print(f"Wrap failed: {e}")


if __name__ == "__main__":
    raise SystemExit(main())
