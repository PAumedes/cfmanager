import typer

from cfmanager.core.exceptions import CFManagerError
from cfmanager.core.output import OutputFormatter
from cfmanager.services.analytics import AnalyticsService

app = typer.Typer(help="View account analytics and usage summaries.", no_args_is_help=True)


@app.command(name="r2", help="Show R2 storage bucket usage summary.")
def r2_usage(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        summary = AnalyticsService(client).r2_usage_summary()
        typer.secho(f"R2 Buckets: {summary['bucket_count']}", bold=True)
        if summary["buckets"]:
            OutputFormatter(output_format).format(
                summary["buckets"],
                headers=["Name", "Location", "Created"],
                keys=["name", "location", "created"],
            )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="zones", help="Show a summary of all zones in the account.")
def zones_summary(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]
    try:
        summary = AnalyticsService(client).zone_summary()
        typer.secho(
            f"Zones: {summary['total_zones']}  Active: {summary['active']}  Paused: {summary['paused']}",
            bold=True,
        )
        OutputFormatter(output_format).format(
            summary["zones"],
            headers=["ID", "Name", "Status", "Paused"],
            keys=["id", "name", "status", "paused"],
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
