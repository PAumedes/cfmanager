from typing import Optional

import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.r2 import R2Service

app = typer.Typer(help="Manage R2 Storage Buckets", no_args_is_help=True)
objects_app = typer.Typer(help="Manage R2 Objects", no_args_is_help=True)
app.add_typer(objects_app, name="objects")

@app.command(name="list", help="List all R2 buckets.")
def list_buckets(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        buckets = r2_service.list_buckets()
        formatter = OutputFormatter(output_format)
        formatter.format(
            buckets,
            headers=["Name", "Creation Date", "Location"],
            keys=["name", "creation_date", "location"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="create", help="Create a new R2 bucket.")
def create_bucket(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="The name of the bucket to create."),
    location_hint: Optional[str] = typer.Option(None, "--location-hint", help="Location hint for the bucket.")
):
    client = ctx.obj["client"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        result = r2_service.create_bucket(name, location_hint)
        typer.secho(f"Successfully created R2 bucket '{name}'", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="delete", help="Delete an R2 bucket.")
def delete_bucket(
    ctx: typer.Context,
    bucket_name: str = typer.Argument(..., help="The name of the bucket to delete."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt.")
):
    client = ctx.obj["client"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete R2 bucket '{bucket_name}'?")
            if not confirm:
                typer.echo("Aborted.")
                raise typer.Exit()

        r2_service.delete_bucket(bucket_name)
        typer.secho(f"Successfully deleted R2 bucket '{bucket_name}'", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="usage", help="Show usage statistics for an R2 bucket.")
def bucket_usage(
    ctx: typer.Context,
    bucket_name: str = typer.Argument(..., help="The name of the bucket.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        usage = r2_service.get_bucket_usage(bucket_name)
        if output_format in ("json", "csv"):
            formatter = OutputFormatter(output_format)
            formatter.format([usage], headers=list(usage.keys()), keys=list(usage.keys()))
        else:
            typer.secho(f"Bucket: {bucket_name}", fg=typer.colors.CYAN, bold=True)
            for key, value in usage.items():
                typer.echo(f"{key}: {value}")
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

# --- objects sub-commands ---

@objects_app.command(name="list", help="List objects in an R2 bucket.")
def list_objects(
    ctx: typer.Context,
    bucket_name: str = typer.Argument(..., help="The name of the bucket."),
    prefix: Optional[str] = typer.Option(None, "--prefix", "-p", help="Filter objects by prefix.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        objects = r2_service.list_objects(bucket_name, prefix)
        formatter = OutputFormatter(output_format)
        formatter.format(
            objects,
            headers=["Key", "Size", "Last Modified", "ETag"],
            keys=["key", "size", "last_modified", "etag"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@objects_app.command(name="upload", help="Upload a file to an R2 bucket.")
def upload_object(
    ctx: typer.Context,
    bucket_name: str = typer.Argument(..., help="The name of the bucket."),
    file_path: str = typer.Argument(..., help="The local file path to upload."),
    object_key: str = typer.Argument(..., help="The object key (path) in the bucket.")
):
    client = ctx.obj["client"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        r2_service.upload_object(bucket_name, file_path, object_key)
        typer.secho(
            f"Successfully uploaded '{file_path}' to '{bucket_name}/{object_key}'",
            fg=typer.colors.GREEN
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@objects_app.command(name="delete", help="Delete an object from an R2 bucket.")
def delete_object(
    ctx: typer.Context,
    bucket_name: str = typer.Argument(..., help="The name of the bucket."),
    object_key: str = typer.Argument(..., help="The object key (path) to delete."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt.")
):
    client = ctx.obj["client"]
    config = ctx.obj["config"]

    r2_service = R2Service(
        client,
        r2_access_key_id=config.r2_access_key_id,
        r2_secret_access_key=config.r2_secret_access_key
    )
    try:
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete '{object_key}' from bucket '{bucket_name}'?"
            )
            if not confirm:
                typer.echo("Aborted.")
                raise typer.Exit()

        r2_service.delete_object(bucket_name, object_key)
        typer.secho(
            f"Successfully deleted '{object_key}' from bucket '{bucket_name}'",
            fg=typer.colors.GREEN
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
