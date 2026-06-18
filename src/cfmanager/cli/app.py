from typing import Optional

import typer

from cfmanager import __version__
from cfmanager.core.client import CloudflareClient
from cfmanager.core.config import Config
from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.logger import setup_logger

app = typer.Typer(
    name="cfm",
    help="Cloudflare Management CLI & TUI",
    no_args_is_help=True
)

def version_callback(value: bool):
    if value:
        typer.echo(f"cfm version {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose debug logging."),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json, csv."),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Use a named credential profile."),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit."
    )
):
    ctx.ensure_object(dict)

    # Load config
    config = Config(profile=profile)
    if verbose:
        config.log_level = "DEBUG"

    setup_logger(config.log_level, config.log_file, dev_mode=config.dev_mode)

    if config.dev_mode:
        typer.secho(f"[cfm dev] debug log → {config.log_file}", fg=typer.colors.CYAN, err=True)
    
    # Skip token validation for `cfm config` subcommands (used to SET the token)
    if ctx.invoked_subcommand != "config":
        try:
            config.validate()
        except CFManagerError as e:
            typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

    client = CloudflareClient(api_token=config.api_token, account_id=config.account_id) if config.api_token else None

    ctx.obj["config"] = config
    ctx.obj["client"] = client
    ctx.obj["output_format"] = output

@app.command(name="tui", help="Launch the interactive TUI dashboard.")
def run_tui(ctx: typer.Context):
    # Launch Textual TUI
    from cfmanager.tui.app import run_tui_app
    run_tui_app()

# Import and register subcommands
from cfmanager.cli import zones, dns
app.add_typer(zones.app, name="zones")
app.add_typer(dns.app, name="dns")

from cfmanager.cli import (
    ssl, r2, pages, loadbalancers, config as config_cli, completion,
    workers, kv, firewall, page_rules, tunnels, email_routing, analytics,
)
app.add_typer(ssl.app, name="ssl")
app.add_typer(r2.app, name="r2")
app.add_typer(pages.app, name="pages")
app.add_typer(loadbalancers.app, name="lb")
app.add_typer(config_cli.app, name="config")
app.add_typer(completion.app, name="completion")
app.add_typer(workers.app, name="workers")
app.add_typer(kv.app, name="kv")
app.add_typer(firewall.app, name="firewall")
app.add_typer(page_rules.app, name="pagerules")
app.add_typer(tunnels.app, name="tunnels")
app.add_typer(email_routing.app, name="email")
app.add_typer(analytics.app, name="analytics")
