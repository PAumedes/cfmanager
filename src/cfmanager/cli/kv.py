import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.workers import KVService

app = typer.Typer(help="Manage Cloudflare KV namespaces.", no_args_is_help=True)


@app.command(name="list", help="List all KV namespaces in the account.")
def list_namespaces(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        namespaces = KVService(client).list_namespaces()
        OutputFormatter(output_format).format(
            namespaces,
            headers=["ID", "Title"],
            keys=["id", "title"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="create", help="Create a KV namespace.")
def create_namespace(
    ctx: typer.Context,
    title: str = typer.Argument(..., help="Namespace title."),
):
    client = ctx.obj["client"]
    try:
        ns = KVService(client).create_namespace(title)
        typer.secho(f"KV namespace '{ns['title']}' created (id: {ns['id']}).", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="delete", help="Delete a KV namespace.")
def delete_namespace(
    ctx: typer.Context,
    namespace_id: str = typer.Argument(..., help="Namespace ID."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
):
    client = ctx.obj["client"]
    try:
        if not force:
            typer.confirm(f"Delete KV namespace '{namespace_id}'?", abort=True)
        KVService(client).delete_namespace(namespace_id)
        typer.secho(f"KV namespace '{namespace_id}' deleted.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
