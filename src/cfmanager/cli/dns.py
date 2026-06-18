import time
from pathlib import Path
from typing import Optional

import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.dns import DNSService
from cfmanager.services.zones import ZoneService

app = typer.Typer(help="Manage DNS Records", no_args_is_help=True)

@app.command(name="list", help="List DNS records for a zone.")
def list_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by record name."),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by record type (A, CNAME, etc.)."),
    watch: Optional[int] = typer.Option(None, "--watch", "-w", help="Refresh every N seconds. Press Ctrl+C to stop."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    dns_service = DNSService(client)

    def _run_once():
        records = dns_service.list_dns_records(zone_id, name=name, type=type)
        formatter = OutputFormatter(output_format)
        formatter.format(
            records,
            headers=["ID", "Name", "Type", "Content", "TTL", "Proxied"],
            keys=["id", "name", "type", "content", "ttl", "proxied"],
        )

    try:
        if watch is None:
            _run_once()
        else:
            while True:
                typer.echo("\033[2J\033[H", nl=False)
                _run_once()
                time.sleep(watch)
    except KeyboardInterrupt:
        pass
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

@app.command(name="export", help="Export DNS records to CSV or BIND zone-file format.")
def export_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv, bind."),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)."),
):
    client = ctx.obj["client"]
    dns_service = DNSService(client)
    try:
        content = dns_service.export_records(zone_id, format=format)
        if output_file:
            Path(output_file).write_text(content)
            typer.secho(f"Exported DNS records to {output_file}", fg=typer.colors.GREEN)
        else:
            typer.echo(content, nl=False)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="import", help="Import DNS records from a CSV or BIND zone-file.")
def import_dns(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    file: str = typer.Option(..., "--file", "-f", help="Input file path (CSV or BIND)."),
    format: str = typer.Option("csv", "--format", help="Import format: csv, bind."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse and validate without creating records."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    dns_service = DNSService(client)
    try:
        content = Path(file).read_text()
        records = dns_service.import_records(zone_id, content, format=format, dry_run=dry_run)
        if dry_run:
            typer.secho(f"[Dry run] Would import {len(records)} record(s):", fg=typer.colors.YELLOW)
            formatter = OutputFormatter(output_format)
            formatter.format(
                records,
                headers=["Name", "Type", "Content", "TTL", "Proxied"],
                keys=["name", "type", "content", "ttl", "proxied"],
            )
        else:
            typer.secho(f"Successfully imported {len(records)} DNS record(s).", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.secho(f"Error: File not found: {file}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="find", help="Search for DNS records by name across all zones.")
def find_dns(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Record name to search for."),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by record type (A, CNAME, etc.)."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    zone_service = ZoneService(client)
    dns_service = DNSService(client)
    try:
        zones = zone_service.list_zones()
        records = dns_service.find_records_across_zones(zones, name=name, type=type)
        if not records:
            typer.secho(f"No records found matching '{name}'.", fg=typer.colors.YELLOW)
            return
        formatter = OutputFormatter(output_format)
        formatter.format(
            records,
            headers=["Zone", "ID", "Name", "Type", "Content", "TTL", "Proxied"],
            keys=["zone_name", "id", "name", "type", "content", "ttl", "proxied"],
        )
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
