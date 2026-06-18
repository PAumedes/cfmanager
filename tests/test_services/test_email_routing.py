"""Tests for EmailRoutingService."""
import pytest
from unittest.mock import MagicMock
from cfmanager.services.email_routing import EmailRoutingService
from cfmanager.core.exceptions import ValidationError


def test_get_email_routing_status(mock_cloudflare_client):
    service = EmailRoutingService(mock_cloudflare_client)

    status = MagicMock()
    status.enabled = True
    status.name = "Email Routing"
    status.tag = "email_routing"
    status.modified_on = "2024-01-01"
    mock_cloudflare_client.sync_client.email_routing.get.return_value = status

    result = service.get_status("zone_123")

    assert result["enabled"] is True
    mock_cloudflare_client.sync_client.email_routing.get.assert_called_once_with(zone_id="zone_123")


def test_list_routing_rules(mock_cloudflare_client):
    service = EmailRoutingService(mock_cloudflare_client)

    rule = MagicMock()
    rule.id = "rule1"
    rule.name = "Catch admins"
    rule.enabled = True
    rule.priority = 1
    rule.matchers = [MagicMock(type="literal", field="to", value="admin@example.com")]
    rule.actions = [MagicMock(type="forward", value=["dest@example.com"])]
    mock_cloudflare_client.sync_client.email_routing.rules.list.return_value = [rule]

    result = service.list_rules("zone_123")

    assert len(result) == 1
    assert result[0]["id"] == "rule1"
    assert result[0]["name"] == "Catch admins"
    assert result[0]["enabled"] is True
    mock_cloudflare_client.sync_client.email_routing.rules.list.assert_called_once_with(
        zone_id="zone_123"
    )


def test_list_destination_addresses(mock_cloudflare_client):
    service = EmailRoutingService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    addr = MagicMock()
    addr.id = "addr1"
    addr.email = "dest@example.com"
    addr.verified = "2024-01-01"
    mock_cloudflare_client.sync_client.email_routing.addresses.list.return_value = [addr]

    result = service.list_addresses()

    assert len(result) == 1
    assert result[0]["email"] == "dest@example.com"
    mock_cloudflare_client.sync_client.email_routing.addresses.list.assert_called_once_with(
        account_id="acc1"
    )


def test_enable_email_routing(mock_cloudflare_client):
    service = EmailRoutingService(mock_cloudflare_client)

    enabled = MagicMock()
    enabled.enabled = True
    mock_cloudflare_client.sync_client.email_routing.enable.return_value = enabled

    result = service.enable("zone_123")
    assert result["enabled"] is True
    mock_cloudflare_client.sync_client.email_routing.enable.assert_called_once_with(
        zone_id="zone_123"
    )


def test_disable_email_routing(mock_cloudflare_client):
    service = EmailRoutingService(mock_cloudflare_client)

    disabled = MagicMock()
    disabled.enabled = False
    mock_cloudflare_client.sync_client.email_routing.disable.return_value = disabled

    result = service.disable("zone_123")
    assert result["enabled"] is False
    mock_cloudflare_client.sync_client.email_routing.disable.assert_called_once_with(
        zone_id="zone_123"
    )
