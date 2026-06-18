"""Tests for cfm workers and cfm kv CLI commands."""
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cfmanager.cli.app import app

runner = CliRunner()

_PATCH_VALIDATE = patch("cfmanager.core.config.Config.validate")
_PATCH_CLIENT = lambda c: patch("cfmanager.core.client.CloudflareClient", return_value=c)


def _mock_client():
    c = MagicMock()
    c.api_token = "tok"
    c.sync_client = MagicMock()
    c.get_account_id.return_value = "acc1"
    return c


# ── workers ───────────────────────────────────────────────────────────────────

def test_workers_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    workers = [{"id": "my-worker", "etag": "abc", "modified_on": "2024-01-01"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.workers.WorkersService.list_workers", return_value=workers),
    ):
        result = runner.invoke(app, ["workers", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "my-worker" in result.output


def test_workers_routes(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    routes = [{"id": "r1", "pattern": "example.com/*", "script": "my-worker"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.workers.WorkersService.list_routes", return_value=routes),
    ):
        result = runner.invoke(app, ["workers", "routes", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "example.com/*" in result.output


def test_workers_delete_with_yes(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.workers.WorkersService.delete_worker", return_value="my-worker") as mock_del,
    ):
        result = runner.invoke(app, ["workers", "delete", "my-worker", "--yes"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_del.assert_called_once_with("my-worker")


# ── kv ────────────────────────────────────────────────────────────────────────

def test_kv_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    namespaces = [{"id": "ns1", "title": "MY_CACHE"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.workers.KVService.list_namespaces", return_value=namespaces),
    ):
        result = runner.invoke(app, ["kv", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "MY_CACHE" in result.output


def test_kv_create(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.workers.KVService.create_namespace", return_value={"id": "ns2", "title": "NEW_NS"}) as mock_create,
    ):
        result = runner.invoke(app, ["kv", "create", "NEW_NS"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_create.assert_called_once_with("NEW_NS")


def test_kv_delete_with_yes(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.workers.KVService.delete_namespace", return_value="ns1") as mock_del,
    ):
        result = runner.invoke(app, ["kv", "delete", "ns1", "--yes"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_del.assert_called_once_with("ns1")
