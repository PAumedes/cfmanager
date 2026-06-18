"""Tests for WorkersService and KVService."""
import pytest
from unittest.mock import MagicMock
from cfmanager.services.workers import WorkersService, KVService
from cfmanager.core.exceptions import APIError


# ── WorkersService ─────────────────────────────────────────────────────────────

def test_list_workers(mock_cloudflare_client):
    service = WorkersService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    script = MagicMock()
    script.id = "my-worker"
    script.etag = "etag123"
    script.modified_on = "2024-01-01T00:00:00Z"
    mock_cloudflare_client.sync_client.workers.scripts.list.return_value = [script]

    result = service.list_workers()

    assert len(result) == 1
    assert result[0]["id"] == "my-worker"
    assert result[0]["etag"] == "etag123"
    mock_cloudflare_client.sync_client.workers.scripts.list.assert_called_once_with(
        account_id="acc1"
    )


def test_list_workers_returns_empty(mock_cloudflare_client):
    service = WorkersService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"
    mock_cloudflare_client.sync_client.workers.scripts.list.return_value = []

    assert service.list_workers() == []


def test_delete_worker(mock_cloudflare_client):
    service = WorkersService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    result = service.delete_worker("my-worker")

    assert result == "my-worker"
    mock_cloudflare_client.sync_client.workers.scripts.delete.assert_called_once_with(
        script_name="my-worker", account_id="acc1"
    )


def test_list_worker_routes(mock_cloudflare_client):
    service = WorkersService(mock_cloudflare_client)

    route = MagicMock()
    route.id = "route1"
    route.pattern = "example.com/*"
    route.script = "my-worker"
    mock_cloudflare_client.sync_client.workers.routes.list.return_value = [route]

    result = service.list_routes("zone_123")

    assert len(result) == 1
    assert result[0]["pattern"] == "example.com/*"
    mock_cloudflare_client.sync_client.workers.routes.list.assert_called_once_with(
        zone_id="zone_123"
    )


# ── KVService ────────────────────────────────────────────────────────────────

def test_list_kv_namespaces(mock_cloudflare_client):
    service = KVService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    ns = MagicMock()
    ns.id = "ns_abc"
    ns.title = "MY_NAMESPACE"
    mock_cloudflare_client.sync_client.kv.namespaces.list.return_value = [ns]

    result = service.list_namespaces()

    assert len(result) == 1
    assert result[0]["id"] == "ns_abc"
    assert result[0]["title"] == "MY_NAMESPACE"
    mock_cloudflare_client.sync_client.kv.namespaces.list.assert_called_once_with(
        account_id="acc1"
    )


def test_create_kv_namespace(mock_cloudflare_client):
    service = KVService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    ns = MagicMock()
    ns.id = "ns_new"
    ns.title = "NEW_NS"
    mock_cloudflare_client.sync_client.kv.namespaces.create.return_value = ns

    result = service.create_namespace("NEW_NS")

    assert result["id"] == "ns_new"
    assert result["title"] == "NEW_NS"
    mock_cloudflare_client.sync_client.kv.namespaces.create.assert_called_once_with(
        account_id="acc1", title="NEW_NS"
    )


def test_delete_kv_namespace(mock_cloudflare_client):
    service = KVService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    result = service.delete_namespace("ns_abc")

    assert result == "ns_abc"
    mock_cloudflare_client.sync_client.kv.namespaces.delete.assert_called_once_with(
        namespace_id="ns_abc", account_id="acc1"
    )
