"""Tests for the @cf_api error-wrapping decorator."""
import asyncio
import pytest
from unittest.mock import MagicMock
from cfmanager.core.decorators import cf_api
from cfmanager.core.exceptions import APIError, ValidationError


class _FakeService:
    def __init__(self):
        self.logger = MagicMock()

    @cf_api("listing things")
    def sync_ok(self):
        return [1, 2, 3]

    @cf_api("creating thing")
    def sync_raises_api_error(self):
        raise APIError("already an APIError")

    @cf_api("deleting thing")
    def sync_raises_validation(self):
        raise ValidationError("bad input")

    @cf_api("fetching thing")
    def sync_raises_generic(self):
        raise RuntimeError("unexpected SDK error")

    @cf_api("listing things async")
    async def async_ok(self):
        return [4, 5, 6]

    @cf_api("fetching thing async")
    async def async_raises_generic(self):
        raise RuntimeError("async unexpected")


def test_sync_passthrough():
    assert _FakeService().sync_ok() == [1, 2, 3]


def test_sync_api_error_reraises_unchanged():
    with pytest.raises(APIError, match="already an APIError"):
        _FakeService().sync_raises_api_error()


def test_sync_validation_error_reraises_unchanged():
    with pytest.raises(ValidationError, match="bad input"):
        _FakeService().sync_raises_validation()


def test_sync_generic_exception_wrapped_as_api_error():
    with pytest.raises(APIError, match="fetching thing"):
        _FakeService().sync_raises_generic()


@pytest.mark.asyncio
async def test_async_passthrough():
    assert await _FakeService().async_ok() == [4, 5, 6]


@pytest.mark.asyncio
async def test_async_generic_exception_wrapped_as_api_error():
    with pytest.raises(APIError, match="fetching thing async"):
        await _FakeService().async_raises_generic()
