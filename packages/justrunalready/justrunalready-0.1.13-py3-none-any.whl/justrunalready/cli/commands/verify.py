"""Verify command implementation."""

import sys
from pathlib import Path

import click
from pydantic import ValidationError

from justrunalready.cli.utils import get_platform_name
from justrunalready.config import load_config
from justrunalready.platforms.loader import get_platform


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
def verify(config: Path, platform: str):
    """Verify bundled dependencies are self-contained."""
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

    rc = platform_impl.verify(cfg)
    sys.exit(rc)
