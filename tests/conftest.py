import pytest
from unittest.mock import MagicMock, AsyncMock
from cfmanager.core.client import CloudflareClient

@pytest.fixture
def mock_cloudflare_client():
    client = MagicMock(spec=CloudflareClient)
    client.api_token = "mock_token"
    
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    
    client.get_account_id.return_value = "mock_account_id"
    client.get_async_account_id = AsyncMock(return_value="mock_account_id")
    client._account_name = "Mock Account"
    
    return client
