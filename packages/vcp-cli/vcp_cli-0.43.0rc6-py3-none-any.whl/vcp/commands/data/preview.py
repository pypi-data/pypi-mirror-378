import webbrowser

import click
from rich.console import Console

from vcp.datasets.api import preview_data_api
from vcp.utils.token import TokenManager

console = Console()
TOKEN_MANAGER = TokenManager()


@click.command("preview")
@click.argument("dataset_id")
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    default=False,
    help="Automatically open the preview URL in your browser",
)
def preview_command(dataset_id: str, open_browser: bool = False):
    """
    Generate a Neuroglancer preview URL for a dataset with zarr files.

    DATASET_ID: The ID of the dataset to preview
    """
    tokens = TOKEN_MANAGER.load_tokens()
    if tokens is None:
        console.print("[red]Tokens not present: Login required[/red]")
        return None

    try:
        # Call the preview API endpoint
        response = preview_data_api(tokens.id_token, dataset_id)

        # Display the preview information
        console.print("[bold green]Dataset Preview Generated[/bold green]")
        console.print(f"Dataset: [bold]{response.dataset_label}[/bold]")
        console.print(f"Dataset ID: {response.dataset_id}")
        console.print(f"Zarr files found: {len(response.zarr_files)}")

        if len(response.zarr_files) > 1:
            console.print(
                f"[yellow]Note: Picking a random zarr file for preview purposes from {len(response.zarr_files)} available[/yellow]"
            )

        console.print("\n[bold blue]Neuroglancer Preview URL:[/bold blue]")
        console.print(f"[link]{response.neuroglancer_url}[/link]")

        if open_browser:
            console.print("\n[green]Opening preview in your default browser...[/green]")
            webbrowser.open(response.neuroglancer_url)
        else:
            console.print(
                "\n[dim]Tip: Use --open to automatically open in browser[/dim]"
            )

    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            console.print(
                "[red]Access denied: You don't have permission to preview this dataset[/red]"
            )
        elif "404" in error_msg:
            console.print(f"[red]{error_msg}[/red]")
        else:
            console.print(f"[red]Error generating preview: {error_msg}[/red]")
