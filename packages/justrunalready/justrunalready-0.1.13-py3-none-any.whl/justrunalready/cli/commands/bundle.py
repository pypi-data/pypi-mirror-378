"""Bundle command implementation."""

import subprocess
import sys
from pathlib import Path

import click
from pydantic import ValidationError

from justrunalready.cli.utils import get_platform_name
from justrunalready.config import load_config
from justrunalready.platforms.loader import get_platform
from justrunalready.wrappers.loader import load_wrappers


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
    help="Optionally wrap the output in a distributable format",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output during bundling",
)
def bundle(config: Path, platform: str, wrap: str, dry_run: bool, verbose: bool):
    """Bundle application into platform-specific layout."""
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

    rc = platform_impl.bundle(
        cfg,
        wrap=wrap,
        dry_run=dry_run,
        verbose=verbose,
    )

    if rc == 0 and wrap:
        _run_wrapper(wrap, cfg, platform_name)

    sys.exit(rc)


def _run_wrapper(name: str, cfg, platform: str) -> None:
    """Run a wrapper on the bundled output."""
    wrappers = load_wrappers()
    wrapper = wrappers.get(name)

    if not wrapper:
        click.echo(f"Wrapper not found: {name}", err=True)
        return

    if not wrapper.supports(platform):
        click.echo(f"Wrapper {name} does not support platform {platform}", err=True)
        return

    try:
        output = wrapper.run(cfg)
        click.echo(f"Wrapped artifact: {output}")
    except subprocess.CalledProcessError as e:
        click.echo(
            f"Wrapper command failed: {e.cmd} (exit code {e.returncode})", err=True
        )
        if e.stderr:
            click.echo(f"Error output: {e.stderr}", err=True)
    except FileNotFoundError as e:
        click.echo(f"Wrapper dependency not found: {e}", err=True)
    except OSError as e:
        click.echo(f"Wrapper I/O error: {e}", err=True)
