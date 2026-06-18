import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.page_rules import PageRulesService

app = typer.Typer(help="Manage Cloudflare Page Rules.", no_args_is_help=True)


@app.command(name="list", help="List page rules for a zone.")
def list_rules(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        rules = PageRulesService(client).list_page_rules(zone_id)
        OutputFormatter(output_format).format(
            rules,
            headers=["ID", "Status", "Target", "Actions"],
            keys=["id", "status", "target", "actions"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="get", help="Get details of a specific page rule.")
def get_rule(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
    rule_id: str = typer.Argument(..., help="Rule ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        rule = PageRulesService(client).get_page_rule(zone_id, rule_id)
        OutputFormatter(output_format).format(
            [rule],
            headers=["ID", "Status", "Target", "Actions"],
            keys=["id", "status", "target", "actions"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="delete", help="Delete a page rule.")
def delete_rule(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
    rule_id: str = typer.Argument(..., help="Rule ID."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
):
    client = ctx.obj["client"]
    try:
        if not force:
            typer.confirm(f"Delete page rule '{rule_id}'?", abort=True)
        PageRulesService(client).delete_page_rule(zone_id, rule_id)
        typer.secho(f"Page rule '{rule_id}' deleted.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
