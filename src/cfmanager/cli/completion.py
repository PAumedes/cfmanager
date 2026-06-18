import subprocess
import sys

import typer

app = typer.Typer(help="Manage shell completion for cfm.", no_args_is_help=True)


def install_shell_completion():
    subprocess.run(
        [sys.executable, "-m", "cfmanager.cli.app", "--install-completion"],
        check=False,
    )


def show_shell_completion():
    subprocess.run(
        [sys.executable, "-m", "cfmanager.cli.app", "--show-completion"],
        check=False,
    )


@app.command(name="install", help="Install shell completion for the current shell.")
def install():
    typer.echo("Installing shell completion…")
    install_shell_completion()
    typer.secho("Done. Restart your shell or source your profile to activate.", fg=typer.colors.GREEN)


@app.command(name="show", help="Print the completion script to stdout.")
def show():
    show_shell_completion()
