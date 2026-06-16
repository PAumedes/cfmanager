import typer
from typing import Optional

from cfmanager.services.dns import DNSService
from cfmanager.core.output import OutputFormatter
from cfmanager.core.exceptions import CFManagerError

app = typer.Typer(help="Manage DNS Records", no_args_is_help=True)

@app.command(name="list", help="List DNS records for a zone.")
def list_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by record name."),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by record type (A, CNAME, etc.).")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    
    dns_service = DNSService(client)
    try:
        records = dns_service.list_dns_records(zone_id, name=name, type=type)
        formatter = OutputFormatter(output_format)
        formatter.format(
            records,
            headers=["ID", "Name", "Type", "Content", "TTL", "Proxied"],
            keys=["id", "name", "type", "content", "ttl", "proxied"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="create", help="Create a DNS record.")
def create_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    name: str = typer.Option(..., "--name", "-n", help="The record name (e.g. api)."),
    type: str = typer.Option(..., "--type", "-t", help="The record type (e.g. A, CNAME)."),
    content: str = typer.Option(..., "--content", "-c", help="The record content (e.g. IP address or target domain)."),
    ttl: int = typer.Option(3600, "--ttl", help="TTL in seconds (default: 3600)."),
    proxied: bool = typer.Option(False, "--proxied", help="Enable Cloudflare proxy.")
):
    client = ctx.obj["client"]
    dns_service = DNSService(client)
    try:
        record = dns_service.create_dns_record(
            zone_id=zone_id,
            name=name,
            type=type,
            content=content,
            ttl=ttl,
            proxied=proxied
        )
        typer.secho(f"Successfully created DNS record {record['id']} ({record['name']})", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="edit", help="Edit a DNS record.")
def edit_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    record_id: str = typer.Argument(..., help="The ID of the record to edit."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New record name."),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="New record type."),
    content: Optional[str] = typer.Option(None, "--content", "-c", help="New record content."),
    ttl: Optional[int] = typer.Option(None, "--ttl", help="New TTL in seconds."),
    proxied: Optional[bool] = typer.Option(None, "--proxied/--no-proxied", help="Enable or disable Cloudflare proxy.")
):
    client = ctx.obj["client"]
    dns_service = DNSService(client)
    try:
        record = dns_service.edit_dns_record(
            zone_id=zone_id,
            record_id=record_id,
            name=name,
            type=type,
            content=content,
            ttl=ttl,
            proxied=proxied
        )
        typer.secho(f"Successfully updated DNS record {record['id']}", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="delete", help="Delete a DNS record.")
def delete_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    record_id: str = typer.Argument(..., help="The ID of the record to delete."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt.")
):
    client = ctx.obj["client"]
    dns_service = DNSService(client)
    try:
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete DNS record {record_id}?")
            if not confirm:
                typer.echo("Aborted.")
                raise typer.Exit()
                
        dns_service.delete_dns_record(zone_id=zone_id, record_id=record_id)
        typer.secho(f"Successfully deleted DNS record {record_id}", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
