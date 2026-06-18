"""Tests for PageRulesService."""
import pytest
from unittest.mock import MagicMock
from cfmanager.services.page_rules import PageRulesService
from cfmanager.core.exceptions import ValidationError


def test_list_page_rules(mock_cloudflare_client):
    service = PageRulesService(mock_cloudflare_client)

    rule = MagicMock()
    rule.id = "pr1"
    rule.status = "active"
    rule.targets = [MagicMock(constraint=MagicMock(operator="matches", value="example.com/*"))]
    rule.actions = [MagicMock(id="always_use_https", value=None)]
    mock_cloudflare_client.sync_client.page_rules.list.return_value = [rule]

    result = service.list_page_rules("zone_123")

    assert len(result) == 1
    assert result[0]["id"] == "pr1"
    assert result[0]["status"] == "active"
    assert "example.com/*" in result[0]["target"]
    mock_cloudflare_client.sync_client.page_rules.list.assert_called_once_with(zone_id="zone_123")


def test_list_page_rules_empty(mock_cloudflare_client):
    service = PageRulesService(mock_cloudflare_client)
    mock_cloudflare_client.sync_client.page_rules.list.return_value = []
    assert service.list_page_rules("zone_123") == []


def test_delete_page_rule(mock_cloudflare_client):
    service = PageRulesService(mock_cloudflare_client)

    result = service.delete_page_rule("zone_123", "pr1")

    assert result == "pr1"
    mock_cloudflare_client.sync_client.page_rules.delete.assert_called_once_with(
        pagerule_id="pr1", zone_id="zone_123"
    )


def test_get_page_rule(mock_cloudflare_client):
    service = PageRulesService(mock_cloudflare_client)

    rule = MagicMock()
    rule.id = "pr1"
    rule.status = "active"
    rule.targets = [MagicMock(constraint=MagicMock(operator="matches", value="example.com/*"))]
    rule.actions = [MagicMock(id="always_use_https", value=None)]
    mock_cloudflare_client.sync_client.page_rules.get.return_value = rule

    result = service.get_page_rule("zone_123", "pr1")

    assert result["id"] == "pr1"
    mock_cloudflare_client.sync_client.page_rules.get.assert_called_once_with(
        pagerule_id="pr1", zone_id="zone_123"
    )
