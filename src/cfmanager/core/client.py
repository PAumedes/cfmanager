from typing import Optional
from cloudflare import Cloudflare, AsyncCloudflare
from cfmanager.core.exceptions import APIError
from cfmanager.core.logger import get_logger

logger = get_logger()

class CloudflareClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self._sync_client: Optional[Cloudflare] = None
        self._async_client: Optional[AsyncCloudflare] = None
        self._account_id: Optional[str] = None
        self._account_name: Optional[str] = None

    @property
    def sync_client(self) -> Cloudflare:
        if self._sync_client is None:
            self._sync_client = Cloudflare(api_token=self.api_token, timeout=30)
        return self._sync_client

    @property
    def async_client(self) -> AsyncCloudflare:
        if self._async_client is None:
            self._async_client = AsyncCloudflare(api_token=self.api_token, timeout=30)
        return self._async_client

    def get_account_id(self) -> str:
        """Get the auto-detected Account ID. Fetches and caches if not present."""
        if self._account_id is not None:
            return self._account_id

        try:
            logger.debug("Auto-detecting Cloudflare account ID...")
            accounts_list = self.sync_client.accounts.list()
            accounts = list(accounts_list)
            
            if not accounts:
                raise APIError("No accounts found for the provided API token.")
            
            first_account = accounts[0]
            self._account_id = first_account.id
            self._account_name = getattr(first_account, 'name', 'Unknown')
            logger.info(f"Auto-detected account: {self._account_name} ({self._account_id})")
            return self._account_id
        except Exception as e:
            logger.exception("Failed to auto-detect account ID")
            raise APIError(f"Cloudflare API error during account detection: {str(e)}") from e

    async def get_async_account_id(self) -> str:
        """Asynchronous version of get_account_id."""
        if self._account_id is not None:
            return self._account_id

        try:
            logger.debug("Auto-detecting Cloudflare account ID asynchronously...")
            accounts_page = await self.async_client.accounts.list()
            
            # Iterate through the async page
            accounts = []
            async for account in accounts_page:
                accounts.append(account)
            
            if not accounts:
                raise APIError("No accounts found for the provided API token.")
            
            first_account = accounts[0]
            self._account_id = first_account.id
            self._account_name = getattr(first_account, 'name', 'Unknown')
            logger.info(f"Auto-detected account: {self._account_name} ({self._account_id})")
            return self._account_id
        except Exception as e:
            logger.exception("Failed to auto-detect account ID asynchronously")
            raise APIError(f"Cloudflare API error during account detection: {str(e)}") from e
