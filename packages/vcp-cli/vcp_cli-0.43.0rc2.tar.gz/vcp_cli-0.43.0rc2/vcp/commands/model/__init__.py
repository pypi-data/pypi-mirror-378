import click
from rich.console import Console

from .download import download_command
from .init import init_command
from .list import list_command
from .stage import stage_command
from .status import status_command
from .submit import submit_command
from .workflow import workflow_command

console = Console()


@click.group()
def model_command():
    """Manage models in the Virtual Cell Platform.

    Available commands:

    \b
    • init     - Initialize a new model project
    • list     - List available models
    • download - Download a specific model version
    • submit   - Submit model metadata to the VCP Model Hub
    • stage    - Stage model data files to Contributions Store
    • status   - Query and display the status of all model submissions
    • workflow - Check workflow status and get step-by-step guidance
    """
    pass


# Add subcommands to the model group
model_command.add_command(list_command, name="list")
model_command.add_command(download_command, name="download")
model_command.add_command(submit_command, name="submit")
model_command.add_command(init_command, name="init")
model_command.add_command(stage_command, name="stage")
model_command.add_command(status_command, name="status")
model_command.add_command(workflow_command, name="workflow")
