from typing import List, Dict, Any

from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError
from cfmanager.core.logger import get_logger

logger = get_logger()


class PagesService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    # --- Sync Methods (for CLI) ---

    def list_projects(self) -> List[Dict[str, Any]]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Listing Pages projects for account {account_id}")
            projects_page = self.client.sync_client.pages.projects.list(account_id=account_id)
            results = []
            for project in projects_page:
                latest_deployment = getattr(project, 'latest_deployment', None)
                latest_stage = getattr(latest_deployment, 'latest_stage', None) if latest_deployment else None
                latest_deployment_status = getattr(latest_stage, 'status', None) if latest_stage else None
                results.append({
                    "name": getattr(project, 'name', None),
                    "domains": getattr(project, 'domains', []),
                    "subdomain": getattr(project, 'subdomain', None),
                    "latest_deployment_status": latest_deployment_status,
                    "created_on": getattr(project, 'created_on', None),
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception("Failed to list Pages projects")
            raise APIError(f"Cloudflare API error listing Pages projects: {str(e)}") from e

    def get_project(self, project_name: str) -> Dict[str, Any]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Getting Pages project '{project_name}'")
            project = self.client.sync_client.pages.projects.get(
                account_id=account_id, project_name=project_name
            )
            latest_deployment = getattr(project, 'latest_deployment', None)
            latest_stage = getattr(latest_deployment, 'latest_stage', None) if latest_deployment else None
            latest_deployment_status = getattr(latest_stage, 'status', None) if latest_stage else None
            return {
                "name": getattr(project, 'name', None),
                "domains": getattr(project, 'domains', []),
                "subdomain": getattr(project, 'subdomain', None),
                "latest_deployment_status": latest_deployment_status,
                "created_on": getattr(project, 'created_on', None),
                "build_config": getattr(project, 'build_config', None),
                "source": getattr(project, 'source', None),
                "deployment_configs": getattr(project, 'deployment_configs', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get Pages project '{project_name}'")
            raise APIError(f"Cloudflare API error getting Pages project: {str(e)}") from e

    def list_deployments(self, project_name: str) -> List[Dict[str, Any]]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Listing deployments for Pages project '{project_name}'")
            deployments_page = self.client.sync_client.pages.projects.deployments.list(
                account_id=account_id, project_name=project_name
            )
            results = []
            for deployment in deployments_page:
                results.append({
                    "id": getattr(deployment, 'id', None),
                    "created_on": getattr(deployment, 'created_on', None),
                    "url": getattr(deployment, 'url', None),
                    "environment": getattr(deployment, 'environment', None),
                    "status": getattr(deployment, 'latest_stage', None) and getattr(
                        getattr(deployment, 'latest_stage', None), 'status', None
                    ),
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to list deployments for Pages project '{project_name}'")
            raise APIError(f"Cloudflare API error listing Pages deployments: {str(e)}") from e

    def rollback_deployment(self, project_name: str, deployment_id: str) -> Dict[str, Any]:
        try:
            account_id = self.client.get_account_id()
            logger.info(
                f"Rolling back Pages project '{project_name}' to deployment '{deployment_id}'"
            )
            result = self.client.sync_client.pages.projects.deployments.rollback(
                account_id=account_id,
                project_name=project_name,
                deployment_id=deployment_id,
            )
            return {
                "project_name": project_name,
                "deployment_id": deployment_id,
                "id": getattr(result, 'id', deployment_id),
                "url": getattr(result, 'url', None),
                "environment": getattr(result, 'environment', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(
                f"Failed to rollback Pages project '{project_name}' to deployment '{deployment_id}'"
            )
            raise APIError(f"Cloudflare API error rolling back Pages deployment: {str(e)}") from e

    # --- Async Methods (for TUI) ---

    async def list_projects_async(self) -> List[Dict[str, Any]]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Listing Pages projects asynchronously for account {account_id}")
            projects_page = await self.client.async_client.pages.projects.list(account_id=account_id)
            results = []
            async for project in projects_page:
                latest_deployment = getattr(project, 'latest_deployment', None)
                latest_stage = getattr(latest_deployment, 'latest_stage', None) if latest_deployment else None
                latest_deployment_status = getattr(latest_stage, 'status', None) if latest_stage else None
                results.append({
                    "name": getattr(project, 'name', None),
                    "domains": getattr(project, 'domains', []),
                    "subdomain": getattr(project, 'subdomain', None),
                    "latest_deployment_status": latest_deployment_status,
                    "created_on": getattr(project, 'created_on', None),
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception("Failed to list Pages projects asynchronously")
            raise APIError(f"Cloudflare API error listing Pages projects: {str(e)}") from e

    async def get_project_async(self, project_name: str) -> Dict[str, Any]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Getting Pages project '{project_name}' asynchronously")
            project = await self.client.async_client.pages.projects.get(
                account_id=account_id, project_name=project_name
            )
            latest_deployment = getattr(project, 'latest_deployment', None)
            latest_stage = getattr(latest_deployment, 'latest_stage', None) if latest_deployment else None
            latest_deployment_status = getattr(latest_stage, 'status', None) if latest_stage else None
            return {
                "name": getattr(project, 'name', None),
                "domains": getattr(project, 'domains', []),
                "subdomain": getattr(project, 'subdomain', None),
                "latest_deployment_status": latest_deployment_status,
                "created_on": getattr(project, 'created_on', None),
                "build_config": getattr(project, 'build_config', None),
                "source": getattr(project, 'source', None),
                "deployment_configs": getattr(project, 'deployment_configs', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get Pages project '{project_name}' asynchronously")
            raise APIError(f"Cloudflare API error getting Pages project: {str(e)}") from e

    async def list_deployments_async(self, project_name: str) -> List[Dict[str, Any]]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Listing deployments asynchronously for Pages project '{project_name}'")
            deployments_page = await self.client.async_client.pages.projects.deployments.list(
                account_id=account_id, project_name=project_name
            )
            results = []
            async for deployment in deployments_page:
                latest_stage = getattr(deployment, 'latest_stage', None)
                results.append({
                    "id": getattr(deployment, 'id', None),
                    "created_on": getattr(deployment, 'created_on', None),
                    "url": getattr(deployment, 'url', None),
                    "environment": getattr(deployment, 'environment', None),
                    "status": getattr(latest_stage, 'status', None) if latest_stage else None,
                })
            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to list deployments asynchronously for Pages project '{project_name}'")
            raise APIError(f"Cloudflare API error listing Pages deployments: {str(e)}") from e

    async def rollback_deployment_async(
        self, project_name: str, deployment_id: str
    ) -> Dict[str, Any]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.info(
                f"Rolling back Pages project '{project_name}' asynchronously to deployment '{deployment_id}'"
            )
            result = await self.client.async_client.pages.projects.deployments.rollback(
                account_id=account_id,
                project_name=project_name,
                deployment_id=deployment_id,
            )
            return {
                "project_name": project_name,
                "deployment_id": deployment_id,
                "id": getattr(result, 'id', deployment_id),
                "url": getattr(result, 'url', None),
                "environment": getattr(result, 'environment', None),
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(
                f"Failed to rollback Pages project '{project_name}' asynchronously to deployment '{deployment_id}'"
            )
            raise APIError(f"Cloudflare API error rolling back Pages deployment: {str(e)}") from e
