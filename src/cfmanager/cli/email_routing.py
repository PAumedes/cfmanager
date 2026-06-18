import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.email_routing import EmailRoutingService

app = typer.Typer(help="Manage Cloudflare Email Routing.", no_args_is_help=True)


@app.command(name="status", help="Show Email Routing status for a zone.")
def status(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        s = EmailRoutingService(client).get_status(zone_id)
        OutputFormatter(output_format).format(
            [s],
            headers=["Enabled", "Name", "Modified"],
            keys=["enabled", "name", "modified_on"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="enable", help="Enable Email Routing for a zone.")
def enable(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    try:
        EmailRoutingService(client).enable(zone_id)
        typer.secho("Email Routing enabled.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="disable", help="Disable Email Routing for a zone.")
def disable(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    try:
        EmailRoutingService(client).disable(zone_id)
        typer.secho("Email Routing disabled.", fg=typer.colors.YELLOW)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="rules", help="List Email Routing rules for a zone.")
def list_rules(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        rules = EmailRoutingService(client).list_rules(zone_id)
        OutputFormatter(output_format).format(
            rules,
            headers=["ID", "Name", "Enabled", "Priority", "Matchers", "Actions"],
            keys=["id", "name", "enabled", "priority", "matchers", "actions"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="addresses", help="List verified destination addresses (account-level).")
def list_addresses(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        addresses = EmailRoutingService(client).list_addresses()
        OutputFormatter(output_format).format(
            addresses,
            headers=["ID", "Email", "Verified"],
            keys=["id", "email", "verified"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
