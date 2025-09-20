"""Main CLI entry point using Click."""

import sys

import click

from justrunalready.cli.commands.bundle import bundle
from justrunalready.cli.commands.info import info
from justrunalready.cli.commands.tree import tree
from justrunalready.cli.commands.verify import verify
from justrunalready.cli.commands.doctor import doctor


@click.group()
@click.version_option()
def cli():
    """JustRunAlready - Cross-platform application bundler."""
    pass


cli.add_command(bundle)
cli.add_command(info)
cli.add_command(tree)
cli.add_command(verify)
cli.add_command(doctor)


if __name__ == "__main__":
    sys.exit(cli())
