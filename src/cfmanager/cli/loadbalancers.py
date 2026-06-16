import typer
from typing import Optional

from cfmanager.services.loadbalancers import LoadBalancerService
from cfmanager.core.output import OutputFormatter
from cfmanager.core.exceptions import CFManagerError

app = typer.Typer(help="Manage Load Balancers", no_args_is_help=True)
pools_app = typer.Typer(help="Manage Load Balancer Pools", no_args_is_help=True)
app.add_typer(pools_app, name="pools")

@app.command(name="list", help="List load balancers for a zone.")
def list_load_balancers(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    lb_service = LoadBalancerService(client)
    try:
        load_balancers = lb_service.list_load_balancers(zone_id)
        formatter = OutputFormatter(output_format)
        formatter.format(
            load_balancers,
            headers=["ID", "Name", "Enabled", "Pools", "Description"],
            keys=["id", "name", "enabled", "default_pools", "description"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="create", help="Create a load balancer for a zone.")
def create_load_balancer(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    name: str = typer.Option(..., "--name", "-n", help="The name (hostname) of the load balancer."),
    pools: str = typer.Option(..., "--pools", help="Comma-separated list of pool IDs (ordered by priority).")
):
    client = ctx.obj["client"]

    pool_list = [p.strip() for p in pools.split(",")]
    lb_service = LoadBalancerService(client)
    try:
        lb = lb_service.create_load_balancer(zone_id, name=name, pools=pool_list)
        typer.secho(
            f"Successfully created load balancer '{name}' ({lb.get('id', '')}) in zone {zone_id}",
            fg=typer.colors.GREEN
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="edit", help="Edit a load balancer.")
def edit_load_balancer(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    lb_id: str = typer.Argument(..., help="The ID of the load balancer to edit."),
    enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", help="Enable or disable the load balancer.")
):
    client = ctx.obj["client"]

    lb_service = LoadBalancerService(client)
    try:
        lb = lb_service.edit_load_balancer(zone_id, lb_id, enabled=enabled)
        typer.secho(f"Successfully updated load balancer {lb_id}", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command(name="delete", help="Delete a load balancer.")
def delete_load_balancer(
    ctx: typer.Context,
    zone_id: str = typer.Argument(..., help="The ID of the zone."),
    lb_id: str = typer.Argument(..., help="The ID of the load balancer to delete."),
    force: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt.")
):
    client = ctx.obj["client"]

    lb_service = LoadBalancerService(client)
    try:
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete load balancer {lb_id}?")
            if not confirm:
                typer.echo("Aborted.")
                raise typer.Exit()

        lb_service.delete_load_balancer(zone_id, lb_id)
        typer.secho(f"Successfully deleted load balancer {lb_id}", fg=typer.colors.GREEN)
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

# --- pools sub-commands ---

@pools_app.command(name="list", help="List all load balancer pools.")
def list_pools(ctx: typer.Context):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    lb_service = LoadBalancerService(client)
    try:
        pools = lb_service.list_pools()
        formatter = OutputFormatter(output_format)
        formatter.format(
            pools,
            headers=["ID", "Name", "Enabled", "Description"],
            keys=["id", "name", "enabled", "description"]
        )
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@pools_app.command(name="health", help="Get health status for a load balancer pool.")
def pool_health(
    ctx: typer.Context,
    pool_id: str = typer.Argument(..., help="The ID of the pool.")
):
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    lb_service = LoadBalancerService(client)
    try:
        health = lb_service.get_pool_health(pool_id)
        if output_format in ("json", "csv"):
            formatter = OutputFormatter(output_format)
            formatter.format([health], headers=list(health.keys()), keys=list(health.keys()))
        else:
            typer.secho(f"Pool Health: {pool_id}", fg=typer.colors.CYAN, bold=True)
            for key, value in health.items():
                typer.echo(f"{key}: {value}")
    except CFManagerError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
