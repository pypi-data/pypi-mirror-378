"""Tree command implementation."""

import sys
from collections import defaultdict
from pathlib import Path
from typing import Set

import click
from pydantic import ValidationError

from justrunalready.cli.utils import get_platform_name
from justrunalready.config import load_config
from justrunalready.inspectors.loader import get_inspector
from justrunalready.platforms.loader import get_platform
from justrunalready.utils import glob_many


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="jra.toml",
    help="Path to jra.toml config file (default: jra.toml)",
)
@click.option(
    "--platform",
    "-p",
    type=click.Choice(["auto", "linux", "macos", "windows"], case_sensitive=False),
    default="auto",
    help="Target platform (default: auto-detect)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["tree", "list"], case_sensitive=False),
    default="tree",
    help="Output format",
)
def tree(config: Path, platform: str, format: str):
    """Show dependency tree for the bundle."""
    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        click.echo(f"Configuration file not found: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        click.echo(f"Configuration validation failed: {e}", err=True)
        sys.exit(1)

    platform_name = get_platform_name(platform)
    platform_impl = get_platform(platform_name)

    if platform_impl is None:
        click.echo(f"Unsupported platform: {platform_name}", err=True)
        sys.exit(2)

    staging = cfg.app.staging_root.resolve()

    if platform_name == "linux":
        if not cfg.layout.linux:
            click.echo("Linux layout not configured", err=True)
            sys.exit(2)
        binary = Path(cfg.layout.linux.binary)
        bin_dir = Path(cfg.layout.linux.bin_dir)
        exe_path = staging / bin_dir / binary
    elif platform_name == "windows":
        if not cfg.layout.windows:
            click.echo("Windows layout not configured", err=True)
            sys.exit(2)
        binary = Path(cfg.layout.windows.binary)
        bin_dir = Path(cfg.layout.windows.bin_dir)
        exe_path = staging / bin_dir / binary
    elif platform_name == "macos":
        if not cfg.layout.macos:
            click.echo("macOS layout not configured", err=True)
            sys.exit(2)
        app_path = cfg.layout.macos.app_bundle
        macos_dir = app_path / "Contents/MacOS"
        if macos_dir.exists():
            import os

            for p in macos_dir.iterdir():
                if p.is_file() and os.access(p, os.X_OK):
                    exe_path = p
                    break
            else:
                click.echo(f"No executable found in {macos_dir}", err=True)
                sys.exit(2)
        else:
            click.echo(f"MacOS directory not found: {macos_dir}", err=True)
            sys.exit(2)
    else:
        click.echo(f"Unsupported platform: {platform_name}", err=True)
        sys.exit(2)

    if not exe_path.exists():
        click.echo(f"Binary not found: {exe_path}", err=True)
        sys.exit(2)

    seed_patterns = cfg.get_platform_includes(platform_name)
    seed_files = glob_many(staging, seed_patterns) if seed_patterns else []

    closure = platform_impl.resolve_closure(cfg, exe_path, seed_files)

    deps_by_lib = defaultdict(set)
    inspector = get_inspector(platform_name)

    if inspector:
        for lib_path in closure:
            if lib_path.exists():
                try:
                    needed = inspector.list_needed(lib_path)
                    for dep in needed:
                        dep_name = Path(dep).name
                        for closed_lib in closure:
                            if closed_lib == lib_path:
                                continue
                            if (
                                closed_lib.name == dep_name
                                or closed_lib.name.startswith(dep_name + ".")
                            ):
                                deps_by_lib[lib_path].add(closed_lib)
                                break
                except (OSError, ValueError):
                    continue

    if format == "tree":
        _print_tree(exe_path, closure, deps_by_lib, staging)
    else:
        _print_list(exe_path, closure, staging)


def _print_tree(exe_path: Path, closure: Set[Path], deps_by_lib: dict, staging: Path):
    """Print dependencies as a tree."""
    click.echo(f"Dependency tree for {exe_path.name}:")
    click.echo(f"Total files in closure: {len(closure)}")
    click.echo()

    def print_node(lib_path: Path, indent: str = "", visited: Set[Path] = None):
        if visited is None:
            visited = set()
        if lib_path in visited:
            click.echo(f"{indent}├── {lib_path.name} [circular]")
            return
        visited.add(lib_path)

        try:
            lib_path.relative_to(staging)
            location = "staging"
        except ValueError:
            if str(lib_path).startswith(("/usr/lib", "/lib")):
                location = "system"
            else:
                location = "other"

        file_size = lib_path.stat().st_size if lib_path.exists() else 0
        size_mb = file_size / 1024 / 1024

        click.echo(f"{indent}├── {lib_path.name} ({size_mb:.2f} MB, {location})")

        deps = sorted(deps_by_lib.get(lib_path, []), key=lambda x: x.name)
        for i, dependency in enumerate(deps):
            is_last = i == len(deps) - 1
            next_indent = indent + ("    " if is_last else "│   ")
            print_node(dependency, next_indent, visited.copy())

    print_node(exe_path)


def _print_list(exe_path: Path, closure: Set[Path], staging: Path):
    """Print dependencies as a list."""
    click.echo(f"Dependency list for {exe_path.name}:")
    click.echo(f"Total files: {len(closure)}")
    click.echo()

    staging_libs = []
    system_libs = []
    other_libs = []

    for lib in sorted(closure, key=lambda x: x.name):
        try:
            lib.relative_to(staging)
            staging_libs.append(lib)
        except ValueError:
            if str(lib).startswith(("/usr/lib", "/lib")):
                system_libs.append(lib)
            else:
                other_libs.append(lib)

    if staging_libs:
        click.echo("From staging:")
        for lib in staging_libs:
            size = lib.stat().st_size if lib.exists() else 0
            click.echo(f"  {lib.name:50} {size/1024/1024:8.2f} MB")

    if system_libs:
        click.echo("\nFrom system (will be bundled):")
        for lib in system_libs:
            size = lib.stat().st_size if lib.exists() else 0
            click.echo(f"  {lib.name:50} {size/1024/1024:8.2f} MB")

    if other_libs:
        click.echo("\nFrom other locations:")
        for lib in other_libs:
            size = lib.stat().st_size if lib.exists() else 0
            click.echo(f"  {lib.name:50} {size/1024/1024:8.2f} MB")

    total_size = sum(lib.stat().st_size for lib in closure if lib.exists())
    click.echo(f"\nTotal size: {total_size/1024/1024:.2f} MB")
