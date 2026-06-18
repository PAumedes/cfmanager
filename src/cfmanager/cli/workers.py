from typing import Optional

import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.workers import WorkersService

app = typer.Typer(help="Manage Cloudflare Workers scripts and routes.", no_args_is_help=True)


@app.command(name="list", help="List all Workers scripts in the account.")
def list_workers(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        workers = WorkersService(client).list_workers()
        OutputFormatter(output_format).format(
            workers,
            headers=["ID", "Modified", "ETag"],
            keys=["id", "modified_on", "etag"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="routes", help="List Workers routes for a zone.")
def list_routes(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        routes = WorkersService(client).list_routes(zone_id)
        OutputFormatter(output_format).format(
            routes,
            headers=["ID", "Pattern", "Script"],
            keys=["id", "pattern", "script"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="delete", help="Delete a Worker script.")
def delete_worker(
    ctx: typer.Context,
    script_name: str = typer.Argument(..., help="Worker script name."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
):
    client = ctx.obj["client"]
    try:
        if not force:
            typer.confirm(f"Delete Worker '{script_name}'?", abort=True)
        WorkersService(client).delete_worker(script_name)
        typer.secho(f"Worker '{script_name}' deleted.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
