"""Tests for FirewallService (IP access rules + WAF package listing)."""
import pytest
from unittest.mock import MagicMock
from cfmanager.services.firewall import FirewallService
from cfmanager.core.exceptions import ValidationError


# ── IP access rules ───────────────────────────────────────────────────────────

def test_list_access_rules(mock_cloudflare_client):
    service = FirewallService(mock_cloudflare_client)

    rule = MagicMock()
    rule.id = "r1"
    rule.mode = "block"
    rule.notes = "bad actor"
    rule.configuration = MagicMock(target="ip", value="1.2.3.4")
    mock_cloudflare_client.sync_client.firewall.access_rules.list.return_value = [rule]

    result = service.list_access_rules("zone_123")

    assert len(result) == 1
    assert result[0]["id"] == "r1"
    assert result[0]["mode"] == "block"
    assert result[0]["target"] == "ip"
    assert result[0]["value"] == "1.2.3.4"
    mock_cloudflare_client.sync_client.firewall.access_rules.list.assert_called_once_with(
        zone_id="zone_123"
    )


def test_create_access_rule(mock_cloudflare_client):
    service = FirewallService(mock_cloudflare_client)

    created = MagicMock()
    created.id = "r2"
    created.mode = "challenge"
    created.notes = ""
    created.configuration = MagicMock(target="ip", value="5.6.7.8")
    mock_cloudflare_client.sync_client.firewall.access_rules.create.return_value = created

    result = service.create_access_rule("zone_123", mode="challenge", target="ip", value="5.6.7.8")

    assert result["id"] == "r2"
    assert result["mode"] == "challenge"
    mock_cloudflare_client.sync_client.firewall.access_rules.create.assert_called_once_with(
        zone_id="zone_123",
        mode="challenge",
        configuration={"target": "ip", "value": "5.6.7.8"},
    )


def test_create_access_rule_invalid_mode_raises(mock_cloudflare_client):
    service = FirewallService(mock_cloudflare_client)
    with pytest.raises(ValidationError, match="mode"):
        service.create_access_rule("zone_123", mode="zap", target="ip", value="1.2.3.4")


def test_delete_access_rule(mock_cloudflare_client):
    service = FirewallService(mock_cloudflare_client)

    result = service.delete_access_rule("zone_123", "r1")

    assert result == "r1"
    mock_cloudflare_client.sync_client.firewall.access_rules.delete.assert_called_once_with(
        identifier="r1", zone_id="zone_123"
    )


# ── WAF packages ──────────────────────────────────────────────────────────────

def test_list_waf_packages(mock_cloudflare_client):
    service = FirewallService(mock_cloudflare_client)

    pkg = MagicMock()
    pkg.id = "pkg1"
    pkg.name = "OWASP ModSecurity"
    pkg.description = "OWASP rules"
    pkg.detection_mode = "traditional"
    mock_cloudflare_client.sync_client.firewall.waf.packages.list.return_value = [pkg]

    result = service.list_waf_packages("zone_123")

    assert len(result) == 1
    assert result[0]["id"] == "pkg1"
    assert result[0]["name"] == "OWASP ModSecurity"
    mock_cloudflare_client.sync_client.firewall.waf.packages.list.assert_called_once_with(
        zone_id="zone_123"
    )
