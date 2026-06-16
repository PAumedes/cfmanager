import pytest
from unittest.mock import MagicMock
from cfmanager.services.dns import DNSService
from cfmanager.core.exceptions import ValidationError

def test_list_dns_records(mock_cloudflare_client):
    service = DNSService(mock_cloudflare_client)
    
    mock_record = MagicMock()
    mock_record.id = "rec_1"
    mock_record.name = "api.example.com"
    mock_record.type = "A"
    mock_record.content = "1.2.3.4"
    mock_record.ttl = 3600
    mock_record.proxied = True
    
    mock_cloudflare_client.sync_client.dns.records.list.return_value = [mock_record]
    
    result = service.list_dns_records("zone_123")
    assert len(result) == 1
    assert result[0]["id"] == "rec_1"
    assert result[0]["proxied"] is True

def test_create_dns_record_success(mock_cloudflare_client):
    service = DNSService(mock_cloudflare_client)
    
    mock_record = MagicMock()
    mock_record.id = "rec_1"
    mock_record.name = "api.example.com"
    mock_record.type = "A"
    mock_record.content = "1.2.3.4"
    mock_record.ttl = 3600
    mock_record.proxied = True
    
    mock_cloudflare_client.sync_client.dns.records.create.return_value = mock_record
    
    result = service.create_dns_record("zone_123", "api", "A", "1.2.3.4", 3600, True)
    assert result["id"] == "rec_1"
    mock_cloudflare_client.sync_client.dns.records.create.assert_called_once_with(
        zone_id="zone_123",
        name="api",
        type="A",
        content="1.2.3.4",
        ttl=3600,
        proxied=True
    )

def test_create_dns_record_validation(mock_cloudflare_client):
    service = DNSService(mock_cloudflare_client)
    
    with pytest.raises(ValidationError):
        service.create_dns_record("zone_123", "", "A", "1.2.3.4")
        
    with pytest.raises(ValidationError):
        service.create_dns_record("zone_123", "api", "INVALID_TYPE", "1.2.3.4")
