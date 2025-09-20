import json
import logging
from typing import Optional

import click
import requests
from rich.console import Console
from rich.table import Table

from ...config.config import Config
from ...utils.token import TokenManager

logger = logging.getLogger(__name__)
console = Console()


@click.command(name="list")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format (table or json)",
)
@click.option("--config", "-c", help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed debug information")
def list_command(format: str, config: Optional[str] = None, verbose: bool = False):
    """List available models and their versions from the VCP Model Hub API."""
    try:
        # Load configuration
        config_data = Config.load(config)

        if verbose:
            console.print("\n[bold blue]Configuration loaded:[/bold blue]")
            console.print(f"Base URL: {config_data.models.base_url}")

        # Check for valid tokens and get auth headers
        token_manager = TokenManager()
        headers = token_manager.get_auth_headers()

        if not headers:
            console.print("[red]Not logged in. Please run 'vcp login' first.[/red]")
            return

        # Use hardcoded list endpoint
        url = f"{config_data.models.base_url}/api/models/list"

        if verbose:
            console.print("\n[bold blue]Debug Information:[/bold blue]")
            console.print(f"API URL: {url}")

        logger.info(f"Making request to {url}")
        response = requests.get(url, headers=headers)
        logger.info(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"API request failed: {response.text}")
            console.print(f"[red]Error: {response.text}[/red]")
            return

        data = response.json()
        logger.info(f"Retrieved {len(data['models'])} models")

        if format == "json":
            console.print(json.dumps(data, indent=2))
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Model Name")
            table.add_column("Version")
            table.add_column("Description")

            for model in data["models"]:
                if model["versions"]:
                    # Add first version with model name
                    first_version = model["versions"][0]
                    table.add_row(
                        model["name"],
                        first_version["version"],
                        first_version["description"],
                    )

                    # Add remaining versions with empty model name
                    for version in model["versions"][1:]:
                        table.add_row(
                            "",
                            version["version"],
                            version["description"],
                        )
                else:
                    # Add model with no versions
                    table.add_row(model["name"], "No versions", "N/A")

            console.print(table)
    except Exception as e:
        logger.error(f"Error in list command: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
