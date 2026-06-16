from typing import Optional

import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.ssl import SSLService

app = typer.Typer(help="Manage SSL/TLS Settings", no_args_is_help=True)

@app.command(name="status", help="Show SSL/TLS status and certificate packs for a zone.")
def ssl_status(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    ssl_service = SSLService(client)
    try:
        setting = ssl_service.get_ssl_setting(zone_id)
        if output_format in ("json", "csv"):
            formatter = OutputFormatter(output_format)
            formatter.format([setting], headers=list(setting.keys()), keys=list(setting.keys()))
        else:
            typer.secho(f"SSL Mode: {setting.get('mode', 'unknown')}", fg=typer.colors.CYAN, bold=True)
            cert_packs = setting.get("certificate_packs", [])
            if cert_packs:
                typer.echo("\nCertificate Packs:")
                formatter = OutputFormatter(output_format)
                formatter.format(
                    cert_packs,
                    headers=["ID", "Type", "Status", "Hosts"],
                    keys=["id", "type", "status", "hosts"]
                )
            else:
                typer.echo("No certificate packs found.")
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="set", help="Set the SSL/TLS mode for a zone.")
def ssl_set(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    mode: str = typer.Option(
        ..., "--mode", "-m",
        help="SSL mode: off, flexible, full, or strict."
    )
):
    valid_modes = ("off", "flexible", "full", "strict")
    if mode not in valid_modes:
        typer.secho(
            f"Error: Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}",
            fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)

    client = ctx.obj["client"]
    ssl_service = SSLService(client)
    try:
        result = ssl_service.set_ssl_mode(zone_id, mode)
        typer.secho(f"Successfully set SSL mode to '{mode}' for zone {zone_id}", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="certs", help="List certificate packs for a zone.")
def ssl_certs(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    ssl_service = SSLService(client)
    try:
        cert_packs = ssl_service.list_cert_packs(zone_id)
        formatter = OutputFormatter(output_format)
        formatter.format(
            cert_packs,
            headers=["ID", "Type", "Status", "Hosts"],
            keys=["id", "type", "status", "hosts"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
