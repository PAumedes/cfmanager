import typer
from typing import Optional

from cfmanager import __version__
from cfmanager.core.config import Config
from cfmanager.core.client import CloudflareClient
from cfmanager.core.logger import setup_logger
from cfmanager.core.exceptions import CFManagerError

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
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit."
    )
):
    ctx.ensure_object(dict)
    
    # Load config
    config = Config()
    if verbose:
        config.log_level = "DEBUG"
        
    setup_logger(config.log_level, config.log_file)
    
    # Validation is skipped if running 'tui' or help since those might not need token initially
    # but for simplicity we validate unless help is requested.
    # Actually, let's validate here, except for --version which is already handled
    try:
        config.validate()
    except CFManagerError as e:
        typer.secho(f"Configuration Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = CloudflareClient(api_token=config.api_token)
    
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

from cfmanager.cli import ssl, r2, pages, loadbalancers
app.add_typer(ssl.app, name="ssl")
app.add_typer(r2.app, name="r2")
app.add_typer(pages.app, name="pages")
app.add_typer(loadbalancers.app, name="lb")
