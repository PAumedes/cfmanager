import asyncio
import functools

from cfmanager.core.exceptions import APIError, ValidationError
from cfmanager.core.logger import get_logger

logger = get_logger()


def cf_api(action: str):
    """Wrap a service method with consistent try/except/log/raise boilerplate.

    Re-raises APIError and ValidationError unchanged. Wraps any other exception
    in APIError with a message that includes *action* for easy diagnosis.

    Works on both sync and async methods.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def sync_wrapper(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except (APIError, ValidationError):
                raise
            except Exception as exc:
                logger.exception(f"Failed {action}")
                raise APIError(f"Cloudflare API error {action}: {exc}") from exc

        @functools.wraps(fn)
        async def async_wrapper(self, *args, **kwargs):
            try:
                return await fn(self, *args, **kwargs)
            except (APIError, ValidationError):
                raise
            except Exception as exc:
                logger.exception(f"Failed {action}")
                raise APIError(f"Cloudflare API error {action}: {exc}") from exc

        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    return decorator
