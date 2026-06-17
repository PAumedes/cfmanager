import pytest
from unittest.mock import MagicMock, AsyncMock
from cfmanager.services.r2 import R2Service
from cfmanager.core.exceptions import ValidationError


def test_list_buckets(mock_cloudflare_client):
    service = R2Service(mock_cloudflare_client)

    mock_bucket = MagicMock()
    mock_bucket.name = "my-bucket"
    mock_bucket.creation_date = "2024-01-01T00:00:00Z"
    mock_bucket.location = "WEUR"

    mock_result = MagicMock()
    mock_result.buckets = [mock_bucket]
    mock_cloudflare_client.sync_client.r2.buckets.list.return_value = mock_result

    result = service.list_buckets()

    assert len(result) == 1
    assert result[0]["name"] == "my-bucket"
    assert result[0]["creation_date"] == "2024-01-01T00:00:00Z"
    assert result[0]["location"] == "WEUR"

    mock_cloudflare_client.sync_client.r2.buckets.list.assert_called_once_with(
        account_id="mock_account_id"
    )


def test_create_bucket(mock_cloudflare_client):
    service = R2Service(mock_cloudflare_client)

    mock_result = MagicMock()
    mock_result.name = "new-bucket"
    mock_result.creation_date = "2024-06-01T00:00:00Z"
    mock_result.location = "ENAM"
    mock_cloudflare_client.sync_client.r2.buckets.create.return_value = mock_result

    result = service.create_bucket("new-bucket", location_hint="ENAM")

    assert result["name"] == "new-bucket"
    assert result["location"] == "ENAM"

    mock_cloudflare_client.sync_client.r2.buckets.create.assert_called_once_with(
        account_id="mock_account_id",
        name="new-bucket",
        location_hint="ENAM",
    )


def test_create_bucket_no_location(mock_cloudflare_client):
    service = R2Service(mock_cloudflare_client)

    mock_result = MagicMock()
    mock_result.name = "simple-bucket"
    mock_result.creation_date = "2024-06-01T00:00:00Z"
    mock_result.location = None
    mock_cloudflare_client.sync_client.r2.buckets.create.return_value = mock_result

    result = service.create_bucket("simple-bucket")

    assert result["name"] == "simple-bucket"
    mock_cloudflare_client.sync_client.r2.buckets.create.assert_called_once_with(
        account_id="mock_account_id",
        name="simple-bucket",
    )


def test_delete_bucket(mock_cloudflare_client):
    service = R2Service(mock_cloudflare_client)

    result = service.delete_bucket("old-bucket")

    assert result == "old-bucket"
    mock_cloudflare_client.sync_client.r2.buckets.delete.assert_called_once_with(
        bucket_name="old-bucket",
        account_id="mock_account_id",
    )


@pytest.mark.asyncio
async def test_list_buckets_async(mock_cloudflare_client):
    service = R2Service(mock_cloudflare_client)

    mock_bucket = MagicMock()
    mock_bucket.name = "async-bucket"
    mock_bucket.creation_date = "2024-01-01T00:00:00Z"
    mock_bucket.location = "APAC"

    mock_result = MagicMock()
    mock_result.buckets = [mock_bucket]
    mock_cloudflare_client.async_client.r2.buckets.list = AsyncMock(
        return_value=mock_result
    )

    result = await service.list_buckets_async()

    assert len(result) == 1
    assert result[0]["name"] == "async-bucket"
    assert result[0]["location"] == "APAC"

    mock_cloudflare_client.async_client.r2.buckets.list.assert_called_once_with(
        account_id="mock_account_id"
    )


def test_list_objects_no_credentials(mock_cloudflare_client):
    service = R2Service(mock_cloudflare_client)
    # No R2 credentials provided — should raise ValidationError
    with pytest.raises(ValidationError):
        service.list_objects("my-bucket")


def test_list_objects_no_credentials_explicit_none(mock_cloudflare_client):
    service = R2Service(
        mock_cloudflare_client,
        r2_access_key_id=None,
        r2_secret_access_key=None,
    )
    with pytest.raises(ValidationError):
        service.list_objects("my-bucket")
