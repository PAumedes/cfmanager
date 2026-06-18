import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.tunnels import TunnelsService

app = typer.Typer(help="Manage Cloudflare Tunnels.", no_args_is_help=True)


@app.command(name="list", help="List all Cloudflare Tunnels in the account.")
def list_tunnels(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        tunnels = TunnelsService(client).list_tunnels()
        OutputFormatter(output_format).format(
            tunnels,
            headers=["ID", "Name", "Status", "Created"],
            keys=["id", "name", "status", "created_at"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="get", help="Get details of a specific Tunnel.")
def get_tunnel(
    ctx: typer.Context,
    tunnel_id: str = typer.Argument(..., help="Tunnel ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        tunnel = TunnelsService(client).get_tunnel(tunnel_id)
        OutputFormatter(output_format).format(
            [tunnel],
            headers=["ID", "Name", "Status", "Created", "Remote Config"],
            keys=["id", "name", "status", "created_at", "remote_config"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
