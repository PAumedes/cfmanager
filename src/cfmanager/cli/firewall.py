from typing import Optional

import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.firewall import FirewallService

app = typer.Typer(help="Manage Cloudflare Firewall rules and WAF.", no_args_is_help=True)


@app.command(name="rules", help="List IP access rules for a zone.")
def list_rules(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        rules = FirewallService(client).list_access_rules(zone_id)
        OutputFormatter(output_format).format(
            rules,
            headers=["ID", "Mode", "Target", "Value", "Notes"],
            keys=["id", "mode", "target", "value", "notes"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="rules-create", help="Create an IP access rule.")
def create_rule(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
    mode: str = typer.Option(..., "--mode", "-m", help="Rule mode: block, challenge, whitelist, …"),
    target: str = typer.Option(..., "--target", "-t", help="Target type: ip, ip_range, country, asn."),
    value: str = typer.Option(..., "--value", "-v", help="Target value (e.g. IP address or country code)."),
    notes: str = typer.Option("", "--notes", help="Optional notes."),
):
    client = ctx.obj["client"]
    try:
        rule = FirewallService(client).create_access_rule(zone_id, mode=mode, target=target, value=value, notes=notes)
        typer.secho(f"Rule created: {rule['id']} ({rule['mode']} {rule['target']}={rule['value']})", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="rules-delete", help="Delete an IP access rule.")
def delete_rule(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
    rule_id: str = typer.Argument(..., help="Rule ID."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
):
    client = ctx.obj["client"]
    try:
        if not force:
            typer.confirm(f"Delete firewall rule '{rule_id}'?", abort=True)
        FirewallService(client).delete_access_rule(zone_id, rule_id)
        typer.secho(f"Rule '{rule_id}' deleted.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="waf", help="List WAF packages for a zone.")
def list_waf(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="Zone ID."),
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        packages = FirewallService(client).list_waf_packages(zone_id)
        OutputFormatter(output_format).format(
            packages,
            headers=["ID", "Name", "Mode", "Description"],
            keys=["id", "name", "detection_mode", "description"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
