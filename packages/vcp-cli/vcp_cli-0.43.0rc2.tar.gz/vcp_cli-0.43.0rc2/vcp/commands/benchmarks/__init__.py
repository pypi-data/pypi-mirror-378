# src/vcp/commands/benchmarks/__init__.py
import click
from rich.console import Console

from .get import get_command
from .list import list_command
from .run import run_command

console = Console()


@click.group()
def benchmarks_command():
    """View and run benchmarks available on the Virtual Cell Platform"""
    pass


# Register subcommands
benchmarks_command.add_command(list_command, name="list")
benchmarks_command.add_command(run_command, name="run")
benchmarks_command.add_command(get_command, name="get")
