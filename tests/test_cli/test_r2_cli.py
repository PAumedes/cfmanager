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


def test_r2_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.r2.R2Service.list_buckets",
            return_value=[
                {"name": "my-bucket", "creation_date": "2024-01-01", "location": "auto"}
            ],
        ),
    ):
        result = runner.invoke(app, ["r2", "list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "my-bucket" in result.output


def test_r2_list_empty(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.r2.R2Service.list_buckets", return_value=[]),
    ):
        result = runner.invoke(app, ["r2", "list"], catch_exceptions=False)

    assert result.exit_code == 0


def test_r2_create(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.r2.R2Service.create_bucket", return_value={"name": "new-bucket"}),
    ):
        result = runner.invoke(
            app, ["r2", "create", "--name", "new-bucket"], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "new-bucket" in result.output


def test_r2_delete(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.r2.R2Service.delete_bucket"),
    ):
        result = runner.invoke(
            app, ["r2", "delete", "my-bucket", "--yes"], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "my-bucket" in result.output


def test_r2_objects_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.r2.R2Service.list_objects",
            return_value=[
                {"key": "data/file.txt", "size": 1024,
                 "last_modified": "2024-01-01", "etag": "abc123"}
            ],
        ),
    ):
        result = runner.invoke(
            app, ["r2", "objects", "list", "my-bucket"], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "data/file.txt" in result.output


def test_r2_list_api_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.r2.R2Service.list_buckets",
            side_effect=APIError("r2 fetch failed"),
        ),
    ):
        result = runner.invoke(app, ["r2", "list"])

    assert result.exit_code == 1
    assert "Error" in result.output
