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


def test_pages_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.pages.PagesService.list_projects",
            return_value=[
                {"name": "my-site", "subdomain": "my-site.pages.dev",
                 "latest_deployment_status": "success"}
            ],
        ),
    ):
        result = runner.invoke(app, ["pages", "list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "my-site" in result.output


def test_pages_list_empty(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.pages.PagesService.list_projects", return_value=[]),
    ):
        result = runner.invoke(app, ["pages", "list"], catch_exceptions=False)

    assert result.exit_code == 0


def test_pages_get(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.pages.PagesService.get_project",
            return_value={
                "name": "my-site",
                "subdomain": "my-site.pages.dev",
                "latest_deployment_status": "success",
            },
        ),
    ):
        result = runner.invoke(app, ["pages", "get", "my-site"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "my-site" in result.output


def test_pages_deployments(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.pages.PagesService.list_deployments",
            return_value=[
                {"id": "deploy_abc", "environment": "production",
                 "status": "success", "url": "https://my-site.pages.dev",
                 "created_on": "2024-01-01"}
            ],
        ),
    ):
        result = runner.invoke(
            app, ["pages", "deployments", "my-site"], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "deploy_abc" in result.output


def test_pages_rollback(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.pages.PagesService.rollback_deployment"),
    ):
        result = runner.invoke(
            app, ["pages", "rollback", "my-site", "deploy_abc", "--yes"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "my-site" in result.output
    assert "deploy_abc" in result.output


def test_pages_list_api_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.pages.PagesService.list_projects",
            side_effect=APIError("pages fetch failed"),
        ),
    ):
        result = runner.invoke(app, ["pages", "list"])

    assert result.exit_code == 1
    assert "Error" in result.output
