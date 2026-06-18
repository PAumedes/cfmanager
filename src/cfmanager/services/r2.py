from typing import List, Dict, Any, Optional

from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError, ValidationError
from cfmanager.core.logger import get_logger

logger = get_logger()

try:
    import boto3
except ImportError:
    boto3 = None


class R2Service:
    def __init__(
        self,
        client: CloudflareClient,
        r2_access_key_id: Optional[str] = None,
        r2_secret_access_key: Optional[str] = None,
    ):
        self.client = client
        self.r2_access_key_id = r2_access_key_id
        self.r2_secret_access_key = r2_secret_access_key

    def _get_s3_client(self):
        if boto3 is None:
            raise ValidationError(
                "boto3 is required for R2 object operations. Install it with: pip install boto3"
            )
        if not self.r2_access_key_id or not self.r2_secret_access_key:
            raise ValidationError(
                "R2 access key ID and secret access key are required for object operations."
            )
        account_id = self.client.get_account_id()
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
        return boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=self.r2_access_key_id,
            aws_secret_access_key=self.r2_secret_access_key,
            region_name="auto",
        )

    # --- Sync Methods (for CLI) ---

    def list_buckets(self) -> List[Dict[str, Any]]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Listing R2 buckets for account {account_id}")
            result = self.client.sync_client.r2.buckets.list(account_id=account_id)
            buckets_iter = getattr(result, 'buckets', result)
            results = []
            for bucket in buckets_iter:
                results.append({
                    "name": getattr(bucket, 'name', None),
                    "creation_date": getattr(bucket, 'creation_date', None),
                    "location": getattr(bucket, 'location', None),
                })
            return results
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception("Failed to list R2 buckets")
            raise APIError(f"Cloudflare API error listing R2 buckets: {str(e)}") from e

    def create_bucket(self, name: str, location_hint: Optional[str] = None) -> Dict[str, Any]:
        try:
            account_id = self.client.get_account_id()
            logger.info(f"Creating R2 bucket '{name}' for account {account_id}")
            params: Dict[str, Any] = {"account_id": account_id, "name": name}
            if location_hint is not None:
                params["location_hint"] = location_hint
            result = self.client.sync_client.r2.buckets.create(**params)
            return {
                "name": getattr(result, 'name', name),
                "creation_date": getattr(result, 'creation_date', None),
                "location": getattr(result, 'location', location_hint),
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to create R2 bucket '{name}'")
            raise APIError(f"Cloudflare API error creating R2 bucket: {str(e)}") from e

    def delete_bucket(self, name: str) -> str:
        try:
            account_id = self.client.get_account_id()
            logger.warning(f"Deleting R2 bucket '{name}' for account {account_id}")
            self.client.sync_client.r2.buckets.delete(
                bucket_name=name, account_id=account_id
            )
            return name
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to delete R2 bucket '{name}'")
            raise APIError(f"Cloudflare API error deleting R2 bucket: {str(e)}") from e

    def get_bucket_usage(self, name: str) -> Dict[str, Any]:
        try:
            account_id = self.client.get_account_id()
            logger.debug(f"Getting usage for R2 bucket '{name}'")
            result = self.client.sync_client.r2.buckets.get(
                bucket_name=name, account_id=account_id
            )
            metrics = getattr(result, 'metrics', {})
            return {
                "name": name,
                "metrics": metrics,
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to get usage for R2 bucket '{name}'")
            raise APIError(f"Cloudflare API error getting R2 bucket usage: {str(e)}") from e

    def list_objects(
        self, bucket_name: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing objects in R2 bucket '{bucket_name}' (prefix={prefix})")
            s3 = self._get_s3_client()
            params: Dict[str, Any] = {"Bucket": bucket_name}
            if prefix is not None:
                params["Prefix"] = prefix
            response = s3.list_objects_v2(**params)
            results = []
            for obj in response.get("Contents", []):
                results.append({
                    "key": obj.get("Key"),
                    "size": obj.get("Size"),
                    "last_modified": obj.get("LastModified"),
                    "etag": obj.get("ETag", "").strip('"'),
                })
            return results
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to list objects in R2 bucket '{bucket_name}'")
            raise APIError(f"R2 error listing objects: {str(e)}") from e

    def delete_object(self, bucket_name: str, key: str) -> str:
        try:
            logger.warning(f"Deleting object '{key}' from R2 bucket '{bucket_name}'")
            s3 = self._get_s3_client()
            s3.delete_object(Bucket=bucket_name, Key=key)
            return key
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to delete object '{key}' from R2 bucket '{bucket_name}'")
            raise APIError(f"R2 error deleting object: {str(e)}") from e

    def upload_object(self, bucket_name: str, file_path: str, object_key: str) -> Dict[str, Any]:
        try:
            logger.info(f"Uploading '{file_path}' to R2 bucket '{bucket_name}' as '{object_key}'")
            s3 = self._get_s3_client()
            s3.upload_file(file_path, bucket_name, object_key)
            return {
                "key": object_key,
                "bucket": bucket_name,
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to upload '{file_path}' to R2 bucket '{bucket_name}'")
            raise APIError(f"R2 error uploading object: {str(e)}") from e

    # --- Async Methods (for TUI) — bucket ops only ---

    async def list_buckets_async(self) -> List[Dict[str, Any]]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Listing R2 buckets asynchronously for account {account_id}")
            result = await self.client.async_client.r2.buckets.list(account_id=account_id)
            buckets_iter = getattr(result, 'buckets', result)
            results = []
            for bucket in buckets_iter:
                results.append({
                    "name": getattr(bucket, 'name', None),
                    "creation_date": getattr(bucket, 'creation_date', None),
                    "location": getattr(bucket, 'location', None),
                })
            return results
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception("Failed to list R2 buckets asynchronously")
            raise APIError(f"Cloudflare API error listing R2 buckets: {str(e)}") from e

    async def create_bucket_async(
        self, name: str, location_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.info(f"Creating R2 bucket '{name}' asynchronously for account {account_id}")
            params: Dict[str, Any] = {"account_id": account_id, "name": name}
            if location_hint is not None:
                params["location_hint"] = location_hint
            result = await self.client.async_client.r2.buckets.create(**params)
            return {
                "name": getattr(result, 'name', name),
                "creation_date": getattr(result, 'creation_date', None),
                "location": getattr(result, 'location', location_hint),
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to create R2 bucket '{name}' asynchronously")
            raise APIError(f"Cloudflare API error creating R2 bucket: {str(e)}") from e

    async def delete_bucket_async(self, name: str) -> str:
        try:
            account_id = await self.client.get_async_account_id()
            logger.warning(f"Deleting R2 bucket '{name}' asynchronously for account {account_id}")
            await self.client.async_client.r2.buckets.delete(
                bucket_name=name, account_id=account_id
            )
            return name
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to delete R2 bucket '{name}' asynchronously")
            raise APIError(f"Cloudflare API error deleting R2 bucket: {str(e)}") from e

    async def list_objects_async(
        self, bucket_name: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        import asyncio
        return await asyncio.to_thread(self.list_objects, bucket_name, prefix)

    async def delete_object_async(self, bucket_name: str, key: str) -> str:
        import asyncio
        return await asyncio.to_thread(self.delete_object, bucket_name, key)

    async def get_bucket_usage_async(self, name: str) -> Dict[str, Any]:
        try:
            account_id = await self.client.get_async_account_id()
            logger.debug(f"Getting usage for R2 bucket '{name}' asynchronously")
            result = await self.client.async_client.r2.buckets.get(
                bucket_name=name, account_id=account_id
            )
            metrics = getattr(result, 'metrics', {})
            return {
                "name": name,
                "metrics": metrics,
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to get usage for R2 bucket '{name}' asynchronously")
            raise APIError(f"Cloudflare API error getting R2 bucket usage: {str(e)}") from e
