from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cfmanager.cli.app import app
from cfmanager.core.exceptions import APIError

runner = CliRunner()


def _make_mock_client():
    client = MagicMock()
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    client.get_account_id.return_value = "mock_account_id"
    return client


def test_lb_list(monkeypatch):
    # Verifies fix 1.4: default_pools is joined, no description column
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.loadbalancers.LoadBalancerService.list_load_balancers",
            return_value=[
                {"id": "lb_1", "name": "lb.example.com", "enabled": True,
                 "default_pools": ["pool_a", "pool_b"], "fallback_pool": "pool_a",
                 "created_on": "2024-01-01"}
            ],
        ),
    ):
        result = runner.invoke(app, ["lb", "list", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "lb.example.com" in result.output
    assert "pool_a, pool_b" in result.output
    # description should not appear as a column header
    assert "Description" not in result.output


def test_lb_create(monkeypatch):
    # Verifies fix 1.1: --fallback-pool required, correct service kwargs
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.loadbalancers.LoadBalancerService.create_load_balancer",
            return_value={"id": "lb_new", "name": "lb.example.com"},
        ) as mock_create,
    ):
        result = runner.invoke(
            app,
            ["lb", "create", "zone_abc",
             "--name", "lb.example.com",
             "--pools", "pool_a,pool_b",
             "--fallback-pool", "pool_a"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "lb_new" in result.output
    # Confirm the service was called with the right positional args
    mock_create.assert_called_once_with(
        "zone_abc", "lb.example.com", ["pool_a", "pool_b"], "pool_a"
    )


def test_lb_create_missing_fallback_pool(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
    ):
        result = runner.invoke(
            app,
            ["lb", "create", "zone_abc", "--name", "lb.example.com", "--pools", "pool_a"],
        )

    # Missing required --fallback-pool should cause a usage error
    assert result.exit_code != 0


def test_lb_edit_enabled(monkeypatch):
    # Verifies fix 1.5: enabled is forwarded when set, not when omitted
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.loadbalancers.LoadBalancerService.edit_load_balancer",
            return_value={"id": "lb_1"},
        ) as mock_edit,
    ):
        result = runner.invoke(
            app, ["lb", "edit", "zone_abc", "lb_1", "--enabled"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    mock_edit.assert_called_once_with("zone_abc", "lb_1", enabled=True)


def test_lb_edit_no_flags_sends_no_enabled(monkeypatch):
    # Verifies fix 1.5: when no --enabled/--disabled given, enabled is NOT passed
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.loadbalancers.LoadBalancerService.edit_load_balancer",
            return_value={"id": "lb_1"},
        ) as mock_edit,
    ):
        result = runner.invoke(
            app, ["lb", "edit", "zone_abc", "lb_1"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    # enabled kwarg must be absent
    call_kwargs = mock_edit.call_args.kwargs
    assert "enabled" not in call_kwargs


def test_lb_delete(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.loadbalancers.LoadBalancerService.delete_load_balancer"),
    ):
        result = runner.invoke(
            app, ["lb", "delete", "zone_abc", "lb_1", "--yes"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "lb_1" in result.output


def test_lb_pools_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.loadbalancers.LoadBalancerService.list_pools",
            return_value=[
                {"id": "pool_a", "name": "us-east", "enabled": True,
                 "description": "US East pool"}
            ],
        ),
    ):
        result = runner.invoke(app, ["lb", "pools", "list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "us-east" in result.output


def test_lb_list_api_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.loadbalancers.LoadBalancerService.list_load_balancers",
            side_effect=APIError("lb fetch failed"),
        ),
    ):
        result = runner.invoke(app, ["lb", "list", "zone_abc"])

    assert result.exit_code == 1
    assert "Error" in result.output
