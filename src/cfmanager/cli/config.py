from typing import Optional

import typer

from cfmanager.core.config import Config
from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.profiles import ProfileManager, ProfileError

app = typer.Typer(help="Manage cfm configuration.", no_args_is_help=True)
profiles_app = typer.Typer(help="Manage named credential profiles.", no_args_is_help=True)
app.add_typer(profiles_app, name="profiles")


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
    typer.echo(f"CFM_ENV               {'dev (DEBUG)' if config.dev_mode else 'production'}")


@app.command(name="path", help="Show the path to the cfm config file.")
def config_path():
    path = Config.config_file()
    typer.echo(str(path))
    if path.exists():
        typer.secho(" (exists)", fg=typer.colors.GREEN)
    else:
        typer.secho(" (not created yet — run 'cfm config set-token' to create it)", fg=typer.colors.YELLOW)


# ── profiles sub-commands ─────────────────────────────────────────────────────

@profiles_app.command(name="list", help="List all saved profiles.")
def profiles_list():
    pm = ProfileManager()
    all_profiles = pm.list_profiles()
    if not all_profiles:
        typer.echo("No profiles saved. Use: cfm config profiles add <name> <token>")
        return
    for name, data in all_profiles.items():
        token = data.get("api_token", "")
        masked = token[:6] + "…" + token[-4:] if len(token) > 10 else "****"
        account = data.get("account_id") or "(auto)"
        typer.echo(f"  {name:<20} token={masked}  account={account}")


@profiles_app.command(name="add", help="Add or update a named profile.")
def profiles_add(
    name: str = typer.Argument(..., help="Profile name."),
    token: str = typer.Argument(..., help="Cloudflare API token for this profile."),
    account_id: Optional[str] = typer.Option(None, "--account-id", help="Pin a specific account ID."),
):
    try:
        pm = ProfileManager()
        pm.add(name, api_token=token, account_id=account_id)
        typer.secho(f"Profile '{name}' saved.", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@profiles_app.command(name="delete", help="Delete a named profile.")
def profiles_delete(
    name: str = typer.Argument(..., help="Profile name to delete."),
):
    try:
        pm = ProfileManager()
        pm.delete(name)
        typer.secho(f"Profile '{name}' deleted.", fg=typer.colors.GREEN)
    except ProfileError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
