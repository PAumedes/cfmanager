import json
from pathlib import Path
from typing import Optional

import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.backup import BackupService
from cfmanager.services.zones import ZoneService

app = typer.Typer(help="Manage Cloudflare Zones (Domains)", no_args_is_help=True)

@app.command(name="list", help="List all Cloudflare zones.")
def list_zones(
    ctx: typer.Context,
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter zones by name.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    
    zone_service = ZoneService(client)
    try:
        zones = zone_service.list_zones(name=name)
        formatter = OutputFormatter(output_format)
        formatter.format(
            zones,
            headers=["ID", "Name", "Status", "Paused", "Type"],
            keys=["id", "name", "status", "paused", "type"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="get", help="Get details of a specific zone.")
def get_zone(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone to retrieve.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    
    zone_service = ZoneService(client)
    try:
        zone = zone_service.get_zone(zone_id)
        if output_format in ("json", "csv"):
            formatter = OutputFormatter(output_format)
            formatter.format([zone], headers=list(zone.keys()), keys=list(zone.keys()))
        else:
            typer.secho(f"Zone Name: {zone['name']}", fg=typer.colors.CYAN, bold=True)
            typer.echo(f"ID: {zone['id']}")
            typer.echo(f"Status: {zone['status']}")
            typer.echo(f"Paused: {'Yes' if zone['paused'] else 'No'}")
            typer.echo(f"Type: {zone['type']}")
            typer.echo(f"Development Mode: {zone['development_mode']}")
            typer.echo(f"Name Servers: {', '.join(zone['name_servers'])}")
            typer.echo(f"Original Name Servers: {', '.join(zone['original_name_servers'])}")
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="delete", help="Delete a specific zone.")
def delete_zone(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone to delete."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    confirm_name: Optional[str] = typer.Option(
        None, "--confirm-name", help="Type the zone name to confirm deletion (matches Cloudflare dashboard guardrail)."
    ),
):
    client = ctx.obj["client"]
    zone_service = ZoneService(client)

    try:
        if force:
            zone_service.delete_zone(zone_id)
        elif confirm_name is not None:
            zone = zone_service.get_zone(zone_id)
            if confirm_name != zone["name"]:
                typer.secho(
                    f"Error: Name '{confirm_name}' does not match zone name '{zone['name']}'. Aborted.",
                    fg=typer.colors.RED, err=True,
                )
                raise typer.Exit(code=1)
            zone_service.delete_zone(zone_id)
        else:
            zone = zone_service.get_zone(zone_id)
            confirm = typer.confirm(f"Are you sure you want to delete zone '{zone['name']}' ({zone_id})?")
            if not confirm:
                typer.echo("Aborted.")
                raise typer.Exit()
            zone_service.delete_zone(zone_id)

        typer.secho(f"Successfully deleted zone {zone_id}", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="backup", help="Backup a zone's DNS records and SSL settings to JSON or YAML.")
def backup_zone(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone to back up."),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)."),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml."),
):
    client = ctx.obj["client"]
    service = BackupService(client)
    try:
        data = service.backup_zone(zone_id)
        if format == "yaml":
            try:
                import yaml
                content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            except ImportError:
                typer.secho("Warning: pyyaml not installed, falling back to JSON.", fg=typer.colors.YELLOW, err=True)
                content = json.dumps(data, indent=2, default=str)
        else:
            content = json.dumps(data, indent=2, default=str)

        if output_file:
            Path(output_file).write_text(content)
            typer.secho(f"Zone backup saved to {output_file}", fg=typer.colors.GREEN)
        else:
            typer.echo(content)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="restore", help="Restore a zone's DNS records and SSL settings from a backup file.")
def restore_zone(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone to restore into."),
    file: str = typer.Option(..., "--file", "-f", help="Backup file path (JSON or YAML)."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be restored without making changes."),
):
    client = ctx.obj["client"]
    service = BackupService(client)
    try:
        raw = Path(file).read_text()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            try:
                import yaml
                data = yaml.safe_load(raw)
            except ImportError:
                typer.secho("Error: file is not valid JSON and pyyaml is not installed.", fg=typer.colors.RED, err=True)
                raise typer.Exit(code=1)
            except Exception as exc:
                typer.secho(f"Error: file is not valid JSON or YAML: {exc}", fg=typer.colors.RED, err=True)
                raise typer.Exit(code=1)

        result = service.restore_zone(zone_id, data, dry_run=dry_run)
        prefix = "[Dry run] Would restore" if dry_run else "Restored"
        typer.secho(
            f"{prefix} {result['dns_created']} DNS record(s)"
            + (", SSL mode set." if result["ssl_set"] else "."),
            fg=typer.colors.YELLOW if dry_run else typer.colors.GREEN,
        )
    except FileNotFoundError:
        typer.secho(f"Error: File not found: {file}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="purge-cache", help="Purge cache for a zone. Supports file URLs, cache tags, hostnames, and URL prefixes.")
def purge_cache(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    all_cache: bool = typer.Option(False, "--all", help="Purge all cached content."),
    files: Optional[str] = typer.Option(None, "--files", help="Comma-separated file URLs to purge."),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated cache tags to purge."),
    hosts: Optional[str] = typer.Option(None, "--hosts", help="Comma-separated hostnames to purge."),
    prefixes: Optional[str] = typer.Option(None, "--prefixes", help="Comma-separated URL prefixes to purge."),
):
    client = ctx.obj["client"]
    zone_service = ZoneService(client)

    if not any([all_cache, files, tags, hosts, prefixes]):
        typer.secho(
            "Error: Specify at least one of --all, --files, --tags, --hosts, --prefixes.",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(code=1)

    def _split(s: Optional[str]):
        return [v.strip() for v in s.split(",")] if s else None

    try:
        zone_service.purge_cache(
            zone_id,
            purge_everything=all_cache,
            files=_split(files),
            tags=_split(tags),
            hosts=_split(hosts),
            prefixes=_split(prefixes),
        )
        typer.secho("Cache purge request submitted successfully.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
