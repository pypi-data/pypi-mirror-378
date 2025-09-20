"""
VCP CLI Model Workflow Status Command

This command provides workflow status checking and guidance for the VCP model workflow.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from ...config.config import Config
from .workflow_assistant import get_workflow_assistant

console = Console()


@click.command()
@click.option(
    "--work-dir",
    help="Path to the model repository work directory (defaults to current directory)",
)
@click.option(
    "--step",
    type=click.Choice([
        "init",
        "status",
        "metadata",
        "weights",
        "package",
        "stage",
        "submit",
    ]),
    help="Get detailed guidance for a specific workflow step",
)
@click.option("--config", "-c", help="Path to config file")
def workflow_command(work_dir: str = None, step: str = None, config: str = None):
    """Check workflow status and get guidance for VCP model commands.

    This command helps you understand where you are in the model workflow
    and what the next steps should be.

    \b
    Examples:
    • vcp model workflow                    # Check current directory status
    • vcp model workflow --work-dir ./my-model  # Check specific directory
    • vcp model workflow --step init        # Get init step guidance
    • vcp model workflow --step metadata  # Get metadata step guidance
    • vcp model workflow --step stage       # Get stage step guidance
    • vcp model workflow --step submit      # Get submit step guidance
    """
    try:
        # Use current directory if work_dir not specified
        if not work_dir:
            work_dir = str(Path.cwd())

        # Load config (same pattern as other model commands)
        config_data = Config.load(config)

        # Get workflow assistant with config
        assistant = get_workflow_assistant(config_data)

        if step:
            # Show specific step guidance
            guidance = assistant.get_step_guidance(step, work_dir)
            console.print(
                Panel(
                    guidance,
                    title=f"[bold blue]Step Guidance: {step.upper()}[/bold blue]",
                )
            )
        else:
            # Show workflow status
            assistant.display_workflow_status(work_dir)

    except Exception as e:
        console.print(f"[red]Error checking workflow status: {e}[/red]")
