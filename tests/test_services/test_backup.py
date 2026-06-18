import json
import pytest
from unittest.mock import MagicMock, patch
from cfmanager.services.backup import BackupService


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    return client


# ── backup_zone ───────────────────────────────────────────────────────────────

def test_backup_zone_returns_full_snapshot(mock_client):
    service = BackupService(mock_client)
    service._zones.get_zone = MagicMock(return_value={"id": "z1", "name": "example.com", "status": "active"})
    service._dns.list_dns_records = MagicMock(return_value=[
        {"id": "r1", "name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False, "comment": ""},
    ])
    service._ssl.get_ssl_setting = MagicMock(return_value={"mode": "full", "zone_id": "z1", "enabled_protocols": [], "certificate_packs": []})

    result = service.backup_zone("z1")

    assert result["zone_id"] == "z1"
    assert result["zone_name"] == "example.com"
    assert result["version"] == 1
    assert len(result["dns_records"]) == 1
    assert result["dns_records"][0]["name"] == "api.example.com"
    assert result["ssl"]["mode"] == "full"


def test_backup_zone_calls_correct_services(mock_client):
    service = BackupService(mock_client)
    service._zones.get_zone = MagicMock(return_value={"id": "z1", "name": "example.com"})
    service._dns.list_dns_records = MagicMock(return_value=[])
    service._ssl.get_ssl_setting = MagicMock(return_value={"mode": "strict", "zone_id": "z1", "enabled_protocols": [], "certificate_packs": []})

    service.backup_zone("z1")

    service._zones.get_zone.assert_called_once_with("z1")
    service._dns.list_dns_records.assert_called_once_with("z1")
    service._ssl.get_ssl_setting.assert_called_once_with("z1")


# ── restore_zone ──────────────────────────────────────────────────────────────

_BACKUP_DATA = {
    "version": 1,
    "zone_id": "z1",
    "zone_name": "example.com",
    "dns_records": [
        {"name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False, "comment": ""},
        {"name": "www.example.com", "type": "CNAME", "content": "example.com", "ttl": 1, "proxied": True, "comment": ""},
    ],
    "ssl": {"mode": "full"},
}


def test_restore_zone_dry_run_counts_without_api_calls(mock_client):
    service = BackupService(mock_client)
    service._dns.create_dns_record = MagicMock()
    service._ssl.set_ssl_mode = MagicMock()

    result = service.restore_zone("z1", _BACKUP_DATA, dry_run=True)

    assert result["dns_created"] == 2
    assert result["ssl_set"] is True
    service._dns.create_dns_record.assert_not_called()
    service._ssl.set_ssl_mode.assert_not_called()


def test_restore_zone_creates_records_and_sets_ssl(mock_client):
    service = BackupService(mock_client)
    service._dns.create_dns_record = MagicMock(return_value={"id": "new_r"})
    service._ssl.set_ssl_mode = MagicMock(return_value={"zone_id": "z1", "mode": "full"})

    result = service.restore_zone("z1", _BACKUP_DATA, dry_run=False)

    assert result["dns_created"] == 2
    assert result["ssl_set"] is True
    assert service._dns.create_dns_record.call_count == 2
    service._ssl.set_ssl_mode.assert_called_once_with("z1", "full")


def test_restore_zone_skips_ssl_if_missing(mock_client):
    service = BackupService(mock_client)
    service._dns.create_dns_record = MagicMock(return_value={"id": "new_r"})
    service._ssl.set_ssl_mode = MagicMock()

    data_no_ssl = {**_BACKUP_DATA, "ssl": {}}
    result = service.restore_zone("z1", data_no_ssl, dry_run=False)

    assert result["ssl_set"] is False
    service._ssl.set_ssl_mode.assert_not_called()


def test_restore_zone_empty_dns_records(mock_client):
    service = BackupService(mock_client)
    service._dns.create_dns_record = MagicMock()
    service._ssl.set_ssl_mode = MagicMock()

    data = {**_BACKUP_DATA, "dns_records": []}
    result = service.restore_zone("z1", data, dry_run=False)

    assert result["dns_created"] == 0
    service._dns.create_dns_record.assert_not_called()


# ── serialisation helpers ─────────────────────────────────────────────────────

def test_backup_to_json_is_valid_json(mock_client):
    service = BackupService(mock_client)
    service._zones.get_zone = MagicMock(return_value={"id": "z1", "name": "example.com"})
    service._dns.list_dns_records = MagicMock(return_value=[])
    service._ssl.get_ssl_setting = MagicMock(return_value={"mode": "off", "zone_id": "z1", "enabled_protocols": [], "certificate_packs": []})

    backup = service.backup_zone("z1")
    json_str = json.dumps(backup)

    parsed = json.loads(json_str)
    assert parsed["zone_name"] == "example.com"
