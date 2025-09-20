import click
from pydantic.fields import Field, FieldInfo
from rich import box
from rich.console import Console
from rich.table import Table

from vcp.datasets.api import CrossModalitySchemaFields, DataItem, search_data_api
from vcp.datasets.download import download_from_candidates_db
from vcp.datasets.download_db import DownloadDatabase
from vcp.utils.token import TokenManager

console = Console()

TOKEN_MANAGER = TokenManager()


# @click.group()
# @click.pass_context
# def data(ctx: click.Context):
#     ctx.ensure_object(dict)
#     ctx.obj["token_manager"] = TokenManager()


def stringify(value):
    """Convert lists/tuples into comma-separated strings, leave other values as str."""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    return str(value)


def format_datasets_as_table(items, title=None):
    """Format search results as a Rich table for console display."""
    if not items:
        return Table()

    # Check if any items have scopes data
    has_scopes = any(getattr(item, "scopes", []) for item in items)

    # Get terminal width and calculate exact column widths
    terminal_width = console.size.width

    # Fixed column widths
    dataset_id_width = 23
    version_width = 8
    namespace_width = 15
    scopes_width = 10 if has_scopes else 0

    # Account for borders and padding (roughly 2 chars per column + table borders)
    padding_overhead = 10 + (5 if has_scopes else 4) * 2  # rough estimate
    fixed_width_total = (
        dataset_id_width
        + version_width
        + namespace_width
        + scopes_width
        + padding_overhead
    )

    # Calculate remaining width for Name column
    name_width = max(20, terminal_width - fixed_width_total)

    # Create the table that expands to terminal width
    tbl = Table(show_header=True, header_style="bold magenta", title=title, expand=True)

    # Add columns with exact calculated widths
    tbl.add_column("Dataset ID", width=dataset_id_width, no_wrap=True)
    tbl.add_column("Version", width=version_width, no_wrap=True)
    tbl.add_column(
        "Namespace", width=namespace_width, no_wrap=True, overflow="ellipsis"
    )

    if has_scopes:
        tbl.add_column("Scopes", width=scopes_width, no_wrap=True, overflow="ellipsis")

    tbl.add_column("Name", width=name_width, overflow="fold", no_wrap=False)

    # Add rows
    for item in items:
        row_values = [item.internal_id or "", item.version or "", item.namespace or ""]

        if has_scopes:
            scopes = getattr(item, "scopes", [])
            row_values.append(stringify(scopes))

        row_values.append(item.name or "")

        tbl.add_row(*row_values)

    return tbl


console = Console()

SEARCH_EXAMPLES = f"""

{click.style("Examples:", fg="cyan", bold=True)} \n
- Search all datasets \n
\t{click.style("vcp data search *", fg="green")} \n
- Search all datasets with a specific namespace \n
\t{click.style('vcp data search tags:"namespace:spermatogenesis"', fg="green")} \n
\t{click.style('vcp data search tags:"namespace:cryoet"', fg="green")} \n
- Search all datasets on a biological field (see below for details)\n
\t{click.style('vcp data search "assay:*microscopy*"', fg="green")} \n
"""


def format_field(name: str, field: FieldInfo):
    col_name = click.style(f"{name}", fg="yellow", bold=True)
    col_desc = click.style(field.description or "", italic=True, fg="white")
    return f"{col_name}\n{col_desc}\n\n"


_searchable_fields_joined = "".join([
    format_field(fn, fi)
    for fn, fi in CrossModalitySchemaFields.__pydantic_fields__.items()
])

SEARCHABLE_FIELDS = f"""
{click.style("Searchable Biological Fields:", fg="cyan", bold=True)} \n
{_searchable_fields_joined}
"""


_other_fields_joined = "".join([
    format_field(fn, fi)
    for fn, fi in [
        (
            "name",
            Field(alias="Name", description="Curator provided name for the dataset"),
        ),
        (
            "tags",
            Field(
                alias="Tags",
                description="List of tags associated with the dataset, including 'namespace:<namespace>'",
            ),
        ),
        (
            "creator",
            Field(
                title="creator",
                alias="Creator",
                description="Stringified list of creators, usually a name e.g. 'John Doe' or organization e.g. 'CZI'",
            ),
        ),
    ]
])

FREE_FIELDS = f"""
{click.style("Searchable Misc Fields:", fg="cyan", bold=True)} \n
{_other_fields_joined}
"""


@click.command(epilog="\n\n".join([SEARCH_EXAMPLES, SEARCHABLE_FIELDS, FREE_FIELDS]))
@click.argument("term")
@click.option(
    "--download",
    is_flag=True,
    help="Download every dataset returned",
)
@click.option(
    "--full",
    is_flag=True,
    help="Show full details for each dataset as a small table",
)
@click.option(
    "-o",
    "--outdir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=str),
    default=".",
    help="Directory for downloaded files (used with --download).",
)
@click.option(
    "--exact",
    is_flag=True,
    help="Match term exactly (no partial matches)",
)
@click.pass_context
def search_command(
    ctx: click.Context,
    term: str,
    download: bool,
    full: bool,
    outdir: str,
    exact: bool,
):
    tokens = TOKEN_MANAGER.load_tokens()
    if tokens is None:
        console.print("[red]Tokens not present: Login required[/red]")
        return

    # When downloading, we will first generate a list of download candidates.
    # We will use SQLite to store such list.
    # Each download request will store the associated query and an expiration date.
    if download:
        db = DownloadDatabase()

        # First, clean up any expired databases.
        removed_count = db.cleanup_expired_databases()
        if removed_count > 0:
            console.print(
                f"🧹 Cleaned up {removed_count} expired candidate database(s)"
            )

        # Check for existing candidates database
        existing_db = db.find_existing_candidates_db(term)

        if existing_db:
            total_candidates, pending_candidates = db.get_database_stats(existing_db)
            completed_candidates = total_candidates - pending_candidates

            console.print(f"📁 Found existing candidates database: {existing_db.name}")
            console.print(
                f"📊 Progress: {completed_candidates}/{total_candidates} downloaded ({pending_candidates} pending)"
            )

            if pending_candidates == 0:
                console.print("✅ All candidates already downloaded!")
                return
            else:
                console.print("🔄 Resuming download from existing candidates...")
                db_path = existing_db
        else:
            console.print("🔍 No existing candidates found, collecting new ones...")
            db_path = db.collect_candidates_from_search(
                query=term,
                id_token=tokens.id_token,
                limit=100,
            )
            total_candidates, pending_candidates = db.get_database_stats(db_path)
            console.print(f"💾 Candidates saved to: {db_path.name}")

        console.print("🚀 Starting downloads...")

        download_from_candidates_db(
            db_path=str(db_path),
            id_token=tokens.id_token,
            outdir=outdir,
        )
        return

    cursor, first = None, True
    current_count = 0  # Track total datasets shown so far

    # state for pagination
    lower_bound = 0  # lower bound estimate of the number of search matches
    page_index = 0
    page_limit = 10  # max number of records per page

    while True:
        resp = search_data_api(tokens.id_token, term, page_limit, cursor, exact)
        cursor = resp.cursor

        if first:
            lower_bound = resp.total

        # Calculate current page bounds
        page_size = len(resp.data)
        current_count += page_size

        if full:
            for item in resp.data:
                tbl = Table(
                    box=box.ASCII,  # <-- pipes for vertical bars
                    show_header=False,  # hide header row since we’re listing field/value pairs
                    pad_edge=False,  # tighten up the padding next to borders
                )
                tbl.add_column("Field", style="bold", no_wrap=True)
                tbl.add_column("Value", overflow="fold")

                fields = [
                    ("Dataset name", item.name),
                    ("Dataset ID", item.internal_id),
                    ("Version", item.version),
                    ("Namespace", item.namespace),
                ]

                # Only add scopes field if it has data
                item_scopes = getattr(item, "scopes", [])
                if item_scopes:
                    fields.append(("Scopes", item_scopes))

                if isinstance(item, DataItem):
                    fields += [
                        ("Assay label", item.assay),
                        ("Assay ontology term ID", item.assay_ontology_term_id),
                        ("Tissue label", item.tissue),
                        ("Tissue ontology term ID", item.tissue_ontology_term_id),
                        ("Organism label", item.organism),
                        ("Organism ontology term ID", item.organism_ontology_term_id),
                        ("Development stage label", item.development_stage),
                        (
                            "Development stage ontology term ID",
                            item.development_stage_ontology_term_id,
                        ),
                        ("Disease label", item.disease),
                        ("Disease ontology term ID", item.disease_ontology_term_id),
                        ("DOI", item.doi),
                        ("License", item.license),
                    ]

                for label, value in fields:
                    tbl.add_row(label, stringify(value))

                console.print(tbl)
                console.print()  # blank line between tables

        # compact table mode
        else:
            # Create pagination title
            _page_start = page_index * page_limit
            _page_length = len(resp.data)
            if page_size > 0:
                title = f"Page {page_index + 1}: Datasets {_page_start + 1}-{_page_start + _page_length} of {lower_bound}"
            else:
                title = "No datasets found"
            console.print(format_datasets_as_table(resp.data, title=title))

        # update state for next page
        page_index += 1
        first = False

        # pagination
        last_page = resp.limit is not None and len(resp.data) < resp.limit
        if not cursor or last_page:
            break

        if not download:
            console.print("\n<RETURN> next page | q + <RETURN> quit")
            if input().strip().lower() == "q":
                break

    console.print("\n✅  End of results.")
