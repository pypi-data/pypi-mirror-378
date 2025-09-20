"""Doctor command for environment diagnostics."""

from __future__ import annotations

import platform as _platform
import shutil
import sys
from typing import List, Tuple

import click

from justrunalready.cli.utils import get_platform_name
from justrunalready.inspectors.loader import load_inspectors
from justrunalready.platforms.loader import load_platforms
from justrunalready.wrappers.loader import load_wrappers


def _check_tool(names: List[str]) -> Tuple[str, bool]:
    """Return (display_name, available)."""
    for n in names:
        if shutil.which(n):
            return (n, True)
    return (names[0], False)


@click.command()
def doctor() -> None:
    """Check environment and tooling for bundling/wrapping."""
    plat = get_platform_name("auto")
    click.echo(f"Platform: {plat}")
    click.echo(f"Python: {sys.version.split()[0]} on {_platform.platform()}")

    plats = load_platforms()
    insp = load_inspectors()
    wraps = load_wrappers()

    click.echo("\nPlugins:")
    click.echo(f"  Platforms: {', '.join(sorted(plats.keys())) or 'none'}")
    click.echo(f"  Inspectors: {', '.join(sorted(insp.keys())) or 'none'}")
    click.echo(f"  Wrappers: {', '.join(sorted(wraps.keys())) or 'none'}")

    click.echo("\nTooling:")
    if plat == "linux":
        for label, choices in (
            ("readelf/ldd", ["readelf", "ldd"]),
            ("patchelf (for rpath)", ["patchelf"]),
            ("appimagetool (wrapper)", ["appimagetool"]),
        ):
            name, ok = _check_tool(choices)
            click.echo(f"  {label:<24} : {'OK' if ok else 'MISSING'} ({name})")
    elif plat == "macos":
        for label, choices in (
            ("otool", ["otool"]),
            ("install_name_tool", ["install_name_tool"]),
            ("hdiutil (wrapper)", ["hdiutil"]),
        ):
            name, ok = _check_tool(choices)
            click.echo(f"  {label:<24} : {'OK' if ok else 'MISSING'} ({name})")
    elif plat == "windows":
        try:
            pe_ok = True
            pe_src = "pefile (python)"
        except Exception:
            pe_ok = False
            pe_src = "pefile (python)"
        name, dumpbin_ok = _check_tool(["dumpbin"])
        click.echo(
            f"  pefile or dumpbin         : {'OK' if pe_ok or dumpbin_ok else 'MISSING'} ({pe_src if pe_ok else name})"
        )
    else:
        click.echo("  (no specific tooling checks for this platform)")

    click.echo("\nNotes:")
    click.echo("  - Optional tools improve results; missing ones may limit features.")
    click.echo("  - Use wrappers only when their required tools are available.")
