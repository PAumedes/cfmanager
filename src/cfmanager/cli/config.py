import typer

from cfmanager.core.config import Config

app = typer.Typer(help="Manage cfm configuration.", no_args_is_help=True)


@app.command(name="set-token", help="Save your Cloudflare API token to ~/.cfmanager/.env")
def set_token(
    token: str = typer.Argument(..., help="Your Cloudflare API token."),
):
    path = Config.save_token(token)
    typer.secho(f"Token saved to {path}", fg=typer.colors.GREEN)
    typer.echo("Run 'cfm zones list' to verify the connection.")


@app.command(name="show", help="Show current configuration (token is masked).")
def show_config():
    config = Config()
    token = config.api_token
    if token:
        if len(token) <= 10:
            masked = "*" * len(token)
        else:
            masked = token[:6] + "*" * (len(token) - 10) + token[-4:]
        typer.secho(f"CLOUDFLARE_API_TOKEN  {masked}", fg=typer.colors.GREEN)
    else:
        typer.secho("CLOUDFLARE_API_TOKEN  (not set)", fg=typer.colors.RED)

    typer.echo(f"R2_ACCESS_KEY_ID      {'(set)' if config.r2_access_key_id else '(not set)'}")
    typer.echo(f"CFM_LOG_LEVEL         {config.log_level}")
    typer.echo(f"CFM_LOG_FILE          {config.log_file}")


@app.command(name="path", help="Show the path to the cfm config file.")
def config_path():
    path = Config.config_file()
    typer.echo(str(path))
    if path.exists():
        typer.secho(" (exists)", fg=typer.colors.GREEN)
    else:
        typer.secho(" (not created yet — run 'cfm config set-token' to create it)", fg=typer.colors.YELLOW)
