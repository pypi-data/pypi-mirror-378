"""Info command implementation."""

import json
import sys
from pathlib import Path

import click
from pydantic import ValidationError

from justrunalready.cli.utils import get_platform_name
from justrunalready.config import load_config


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
    "--wrap",
    "-w",
    type=click.Choice(["appimage", "dmg", "zip"], case_sensitive=False),
    help="Optional wrapper format",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["env", "json"], case_sensitive=False),
    default="env",
    help="Output format",
)
def info(config: Path, platform: str, wrap: str, format: str):
    """Print resolved bundle and artifact information."""
    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        click.echo(f"Configuration file not found: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        click.echo(f"Configuration validation failed: {e}", err=True)
        sys.exit(1)

    platform_name = get_platform_name(platform)

    name = cfg.app.name
    staging_root = str(cfg.app.staging_root)

    bundle_path = ""
    binary_path = ""

    if platform_name == "linux":
        if cfg.layout.linux:
            bundle_path = str(cfg.layout.linux.appdir)
            binary_path = str(
                cfg.layout.linux.appdir
                / cfg.layout.linux.bin_dir
                / cfg.layout.linux.binary
            )
    elif platform_name == "macos":
        if cfg.layout.macos:
            bundle_path = str(cfg.layout.macos.app_bundle)
            macos_bin = (
                cfg.layout.macos.binary if cfg.layout.macos.binary is not None else name
            )
            binary_path = str(
                cfg.layout.macos.app_bundle / "Contents/MacOS" / macos_bin
            )
    elif platform_name == "windows":
        if cfg.layout.windows:
            bundle_path = str(cfg.app.staging_root / cfg.layout.windows.bin_dir)
            binary_path = str(
                cfg.app.staging_root
                / cfg.layout.windows.bin_dir
                / cfg.layout.windows.binary
            )

    artifact_path = ""
    if wrap:
        wrap = wrap.lower()
        if wrap == "appimage" and platform_name == "linux":
            artifact_path = f"{name}-linux-x86_64.AppImage"
        elif wrap == "dmg" and platform_name == "macos":
            artifact_path = f"{name}-macos.dmg"
        elif wrap == "zip":
            artifact_path = f"{name}-{platform_name}.zip"

    if format == "json":
        output = {
            "name": name,
            "platform": platform_name,
            "staging_root": staging_root,
            "bundle_path": bundle_path,
            "binary_path": binary_path,
            "artifact_path": artifact_path if artifact_path else None,
            "wrapper": wrap if wrap else None,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(f"name={name}")
        click.echo(f"platform={platform_name}")
        click.echo(f"staging_root={staging_root}")
        click.echo(f"bundle_path={bundle_path}")
        click.echo(f"binary_path={binary_path}")
        if artifact_path:
            click.echo(f"artifact_path={artifact_path}")
        if wrap:
            click.echo(f"wrapper={wrap}")
