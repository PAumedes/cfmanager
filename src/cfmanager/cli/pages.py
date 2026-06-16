import typer
from typing import Optional

from cfmanager.services.pages import PagesService
from cfmanager.core.output import OutputFormatter
from cfmanager.core.exceptions import CFManagerError

app = typer.Typer(help="Manage Cloudflare Pages", no_args_is_help=True)

@app.command(name="list", help="List all Cloudflare Pages projects.")
def list_projects(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    pages_service = PagesService(client)
    try:
        projects = pages_service.list_projects()
        formatter = OutputFormatter(output_format)
        formatter.format(
            projects,
            headers=["Name", "Subdomain", "Latest Deployment Status"],
            keys=["name", "subdomain", "latest_deployment_status"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="get", help="Get details of a specific Pages project.")
def get_project(
    ctx: typer.Context,
    project_name: str = typer.Argument(..., help="The name of the Pages project.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    pages_service = PagesService(client)
    try:
        project = pages_service.get_project(project_name)
        if output_format in ("json", "csv"):
            formatter = OutputFormatter(output_format)
            formatter.format([project], headers=list(project.keys()), keys=list(project.keys()))
        else:
            typer.secho(f"Project: {project.get('name', project_name)}", fg=typer.colors.CYAN, bold=True)
            for key, value in project.items():
                typer.echo(f"{key}: {value}")
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="deployments", help="List deployments for a Pages project.")
def list_deployments(
    ctx: typer.Context,
    project_name: str = typer.Argument(..., help="The name of the Pages project.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    pages_service = PagesService(client)
    try:
        deployments = pages_service.list_deployments(project_name)
        formatter = OutputFormatter(output_format)
        formatter.format(
            deployments,
            headers=["ID", "Environment", "Status", "URL", "Created On"],
            keys=["id", "environment", "status", "url", "created_on"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="rollback", help="Rollback a Pages project to a specific deployment.")
def rollback_deployment(
    ctx: typer.Context,
    project_name: str = typer.Argument(..., help="The name of the Pages project."),
    deployment_id: str = typer.Argument(..., help="The ID of the deployment to roll back to."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt.")
):
    client = ctx.obj["client"]

    pages_service = PagesService(client)
    try:
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to rollback project '{project_name}' to deployment {deployment_id}?"
            )
            if not confirm:
                typer.echo("Aborted.")
                raise typer.Exit()

        pages_service.rollback_deployment(project_name, deployment_id)
        typer.secho(
            f"Successfully rolled back project '{project_name}' to deployment {deployment_id}",
            fg=typer.colors.GREEN
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
