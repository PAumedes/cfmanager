import pytest
from unittest.mock import MagicMock, AsyncMock
from cfmanager.services.pages import PagesService


def test_list_projects(mock_cloudflare_client):
    service = PagesService(mock_cloudflare_client)

    mock_project = MagicMock()
    mock_project.name = "my-site"
    mock_project.domains = ["my-site.pages.dev"]
    mock_project.subdomain = "my-site"
    mock_project.created_on = "2024-01-01T00:00:00Z"
    # latest_deployment chain
    mock_latest_stage = MagicMock()
    mock_latest_stage.status = "success"
    mock_latest_deployment = MagicMock()
    mock_latest_deployment.latest_stage = mock_latest_stage
    mock_project.latest_deployment = mock_latest_deployment

    mock_cloudflare_client.sync_client.pages.projects.list.return_value = [mock_project]

    result = service.list_projects()

    assert len(result) == 1
    assert result[0]["name"] == "my-site"
    assert result[0]["subdomain"] == "my-site"
    assert result[0]["latest_deployment_status"] == "success"

    mock_cloudflare_client.sync_client.pages.projects.list.assert_called_once_with(
        account_id="mock_account_id"
    )


def test_get_project(mock_cloudflare_client):
    service = PagesService(mock_cloudflare_client)

    mock_project = MagicMock()
    mock_project.name = "my-site"
    mock_project.domains = ["my-site.pages.dev"]
    mock_project.subdomain = "my-site"
    mock_project.created_on = "2024-01-01T00:00:00Z"
    mock_project.build_config = {"build_command": "npm run build"}
    mock_project.source = {"type": "github"}
    mock_project.deployment_configs = {}
    mock_latest_stage = MagicMock()
    mock_latest_stage.status = "success"
    mock_latest_deployment = MagicMock()
    mock_latest_deployment.latest_stage = mock_latest_stage
    mock_project.latest_deployment = mock_latest_deployment

    mock_cloudflare_client.sync_client.pages.projects.get.return_value = mock_project

    result = service.get_project("my-site")

    assert result["name"] == "my-site"
    assert result["subdomain"] == "my-site"
    assert result["latest_deployment_status"] == "success"
    assert result["build_config"] == {"build_command": "npm run build"}

    mock_cloudflare_client.sync_client.pages.projects.get.assert_called_once_with(
        account_id="mock_account_id",
        project_name="my-site",
    )


def test_list_deployments(mock_cloudflare_client):
    service = PagesService(mock_cloudflare_client)

    mock_deployment = MagicMock()
    mock_deployment.id = "deploy_abc"
    mock_deployment.created_on = "2024-06-01T12:00:00Z"
    mock_deployment.url = "https://abc.my-site.pages.dev"
    mock_deployment.environment = "production"
    mock_latest_stage = MagicMock()
    mock_latest_stage.status = "success"
    mock_deployment.latest_stage = mock_latest_stage

    mock_cloudflare_client.sync_client.pages.projects.deployments.list.return_value = [
        mock_deployment
    ]

    result = service.list_deployments("my-site")

    assert len(result) == 1
    assert result[0]["id"] == "deploy_abc"
    assert result[0]["environment"] == "production"
    assert result[0]["url"] == "https://abc.my-site.pages.dev"

    mock_cloudflare_client.sync_client.pages.projects.deployments.list.assert_called_once_with(
        account_id="mock_account_id",
        project_name="my-site",
    )


def test_rollback_deployment(mock_cloudflare_client):
    service = PagesService(mock_cloudflare_client)

    mock_result = MagicMock()
    mock_result.id = "deploy_old"
    mock_result.url = "https://old.my-site.pages.dev"
    mock_result.environment = "production"
    mock_cloudflare_client.sync_client.pages.projects.deployments.rollback.return_value = (
        mock_result
    )

    result = service.rollback_deployment("my-site", "deploy_old")

    assert result["project_name"] == "my-site"
    assert result["deployment_id"] == "deploy_old"
    assert result["id"] == "deploy_old"
    assert result["url"] == "https://old.my-site.pages.dev"

    mock_cloudflare_client.sync_client.pages.projects.deployments.rollback.assert_called_once_with(
        account_id="mock_account_id",
        project_name="my-site",
        deployment_id="deploy_old",
    )


@pytest.mark.asyncio
async def test_list_projects_async(mock_cloudflare_client):
    service = PagesService(mock_cloudflare_client)

    mock_project = MagicMock()
    mock_project.name = "async-site"
    mock_project.domains = ["async-site.pages.dev"]
    mock_project.subdomain = "async-site"
    mock_project.created_on = "2024-01-01T00:00:00Z"
    mock_latest_stage = MagicMock()
    mock_latest_stage.status = "failure"
    mock_latest_deployment = MagicMock()
    mock_latest_deployment.latest_stage = mock_latest_stage
    mock_project.latest_deployment = mock_latest_deployment

    class AsyncPage:
        def __aiter__(self):
            return self

        async def __anext__(self):
            if not hasattr(self, "_done"):
                self._done = True
                return mock_project
            raise StopAsyncIteration

    mock_cloudflare_client.async_client.pages.projects.list = AsyncMock(
        return_value=AsyncPage()
    )

    result = await service.list_projects_async()

    assert len(result) == 1
    assert result[0]["name"] == "async-site"
    assert result[0]["latest_deployment_status"] == "failure"
