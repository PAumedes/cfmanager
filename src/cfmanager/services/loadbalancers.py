from typing import List, Dict, Any, Optional
from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError
from cfmanager.core.logger import get_logger

logger = get_logger()


class LoadBalancerService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    # --- Sync Methods (for CLI) ---

    def list_load_balancers(self, zone_id: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing load balancers for zone {zone_id}")
            lbs_page = self.client.sync_client.load_balancers.list(zone_id=zone_id)
            results = []
            for lb in lbs_page:
                results.append({
                    "id": getattr(lb, 'id', None),
                    "name": getattr(lb, 'name', None),
                    "enabled": getattr(lb, 'enabled', None),
                    "fallback_pool": getattr(lb, 'fallback_pool', None),
                    "default_pools": getattr(lb, 'default_pools', []),
                    "created_on": getattr(lb, 'created_on', None),
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to list load balancers for zone {zone_id}")
            raise APIError(f"Cloudflare API error listing load balancers: {str(e)}") from e

    def create_load_balancer(
        self,
        zone_id: str,
        name: str,
        default_pools: List[str],
        fallback_pool: str,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Creating load balancer '{name}' for zone {zone_id}")
            lb = self.client.sync_client.load_balancers.create(
                zone_id=zone_id,
                name=name,
                default_pools=default_pools,
                fallback_pool=fallback_pool,
                enabled=enabled,
            )
            return {
                "id": getattr(lb, 'id', None),
                "name": getattr(lb, 'name', name),
                "enabled": getattr(lb, 'enabled', enabled),
                "fallback_pool": getattr(lb, 'fallback_pool', fallback_pool),
                "default_pools": getattr(lb, 'default_pools', default_pools),
                "created_on": getattr(lb, 'created_on', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to create load balancer '{name}' for zone {zone_id}")
            raise APIError(f"Cloudflare API error creating load balancer: {str(e)}") from e

    def edit_load_balancer(self, zone_id: str, lb_id: str, **kwargs) -> Dict[str, Any]:
        try:
            logger.info(f"Editing load balancer '{lb_id}' in zone {zone_id}")
            lb = self.client.sync_client.load_balancers.update(
                load_balancer_id=lb_id,
                zone_id=zone_id,
                **kwargs,
            )
            return {
                "id": getattr(lb, 'id', lb_id),
                "name": getattr(lb, 'name', None),
                "enabled": getattr(lb, 'enabled', None),
                "fallback_pool": getattr(lb, 'fallback_pool', None),
                "default_pools": getattr(lb, 'default_pools', []),
                "created_on": getattr(lb, 'created_on', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to edit load balancer '{lb_id}' in zone {zone_id}")
            raise APIError(f"Cloudflare API error editing load balancer: {str(e)}") from e

    def delete_load_balancer(self, zone_id: str, lb_id: str) -> str:
        try:
            logger.warning(f"Deleting load balancer '{lb_id}' in zone {zone_id}")
            self.client.sync_client.load_balancers.delete(
                load_balancer_id=lb_id, zone_id=zone_id
            )
            return lb_id
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to delete load balancer '{lb_id}' in zone {zone_id}")
            raise APIError(f"Cloudflare API error deleting load balancer: {str(e)}") from e

    def list_pools(self) -> List[Dict[str, Any]]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Listing load balancer pools for account {account_id}")
            pools_page = self.client.sync_client.load_balancers.pools.list(account_id=account_id)
            results = []
            for pool in pools_page:
                origins = getattr(pool, 'origins', [])
                results.append({
                    "id": getattr(pool, 'id', None),
                    "name": getattr(pool, 'name', None),
                    "enabled": getattr(pool, 'enabled', None),
                    "description": getattr(pool, 'description', None),
                    "origins": origins,
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception("Failed to list load balancer pools")
            raise APIError(f"Cloudflare API error listing load balancer pools: {str(e)}") from e

    def get_pool_health(self, pool_id: str) -> Dict[str, Any]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Getting health for pool '{pool_id}'")
            health = self.client.sync_client.load_balancers.pools.health(
                pool_id=pool_id, account_id=account_id
            )
            return {
                "pool_id": pool_id,
                "status": getattr(health, 'status', None),
                "origins": getattr(health, 'origins', {}),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get health for pool '{pool_id}'")
            raise APIError(f"Cloudflare API error getting pool health: {str(e)}") from e

    # --- Async Methods (for TUI) ---

    async def list_load_balancers_async(self, zone_id: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing load balancers asynchronously for zone {zone_id}")
            lbs_page = await self.client.async_client.load_balancers.list(zone_id=zone_id)
            results = []
            async for lb in lbs_page:
                results.append({
                    "id": getattr(lb, 'id', None),
                    "name": getattr(lb, 'name', None),
                    "enabled": getattr(lb, 'enabled', None),
                    "fallback_pool": getattr(lb, 'fallback_pool', None),
                    "default_pools": getattr(lb, 'default_pools', []),
                    "created_on": getattr(lb, 'created_on', None),
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to list load balancers asynchronously for zone {zone_id}")
            raise APIError(f"Cloudflare API error listing load balancers: {str(e)}") from e

    async def create_load_balancer_async(
        self,
        zone_id: str,
        name: str,
        default_pools: List[str],
        fallback_pool: str,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Creating load balancer '{name}' asynchronously for zone {zone_id}")
            lb = await self.client.async_client.load_balancers.create(
                zone_id=zone_id,
                name=name,
                default_pools=default_pools,
                fallback_pool=fallback_pool,
                enabled=enabled,
            )
            return {
                "id": getattr(lb, 'id', None),
                "name": getattr(lb, 'name', name),
                "enabled": getattr(lb, 'enabled', enabled),
                "fallback_pool": getattr(lb, 'fallback_pool', fallback_pool),
                "default_pools": getattr(lb, 'default_pools', default_pools),
                "created_on": getattr(lb, 'created_on', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to create load balancer '{name}' asynchronously for zone {zone_id}")
            raise APIError(f"Cloudflare API error creating load balancer: {str(e)}") from e

    async def edit_load_balancer_async(
        self, zone_id: str, lb_id: str, **kwargs
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Editing load balancer '{lb_id}' asynchronously in zone {zone_id}")
            lb = await self.client.async_client.load_balancers.update(
                load_balancer_id=lb_id,
                zone_id=zone_id,
                **kwargs,
            )
            return {
                "id": getattr(lb, 'id', lb_id),
                "name": getattr(lb, 'name', None),
                "enabled": getattr(lb, 'enabled', None),
                "fallback_pool": getattr(lb, 'fallback_pool', None),
                "default_pools": getattr(lb, 'default_pools', []),
                "created_on": getattr(lb, 'created_on', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to edit load balancer '{lb_id}' asynchronously in zone {zone_id}")
            raise APIError(f"Cloudflare API error editing load balancer: {str(e)}") from e

    async def delete_load_balancer_async(self, zone_id: str, lb_id: str) -> str:
        try:
            logger.warning(f"Deleting load balancer '{lb_id}' asynchronously in zone {zone_id}")
            await self.client.async_client.load_balancers.delete(
                load_balancer_id=lb_id, zone_id=zone_id
            )
            return lb_id
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to delete load balancer '{lb_id}' asynchronously in zone {zone_id}")
            raise APIError(f"Cloudflare API error deleting load balancer: {str(e)}") from e

    async def list_pools_async(self) -> List[Dict[str, Any]]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Listing load balancer pools asynchronously for account {account_id}")
            pools_page = await self.client.async_client.load_balancers.pools.list(
                account_id=account_id
            )
            results = []
            async for pool in pools_page:
                origins = getattr(pool, 'origins', [])
                results.append({
                    "id": getattr(pool, 'id', None),
                    "name": getattr(pool, 'name', None),
                    "enabled": getattr(pool, 'enabled', None),
                    "description": getattr(pool, 'description', None),
                    "origins": origins,
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception("Failed to list load balancer pools asynchronously")
            raise APIError(f"Cloudflare API error listing load balancer pools: {str(e)}") from e

    async def get_pool_health_async(self, pool_id: str) -> Dict[str, Any]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Getting health for pool '{pool_id}' asynchronously")
            health = await self.client.async_client.load_balancers.pools.health(
                pool_id=pool_id, account_id=account_id
            )
            return {
                "pool_id": pool_id,
                "status": getattr(health, 'status', None),
                "origins": getattr(health, 'origins', {}),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get health for pool '{pool_id}' asynchronously")
            raise APIError(f"Cloudflare API error getting pool health: {str(e)}") from e
