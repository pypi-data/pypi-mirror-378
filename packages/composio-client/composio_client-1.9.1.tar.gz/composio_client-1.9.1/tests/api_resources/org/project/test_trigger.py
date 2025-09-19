# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from composio_client import Composio, AsyncComposio
from composio_client.types.org.project import TriggerListResponse, TriggerUpdateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTrigger:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_update(self, client: Composio) -> None:
        trigger = client.org.project.trigger.update()
        assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Composio) -> None:
        trigger = client.org.project.trigger.update(
            enabled=True,
        )
        assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Composio) -> None:
        response = client.org.project.trigger.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trigger = response.parse()
        assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Composio) -> None:
        with client.org.project.trigger.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trigger = response.parse()
            assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Composio) -> None:
        trigger = client.org.project.trigger.list()
        assert_matches_type(TriggerListResponse, trigger, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Composio) -> None:
        response = client.org.project.trigger.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trigger = response.parse()
        assert_matches_type(TriggerListResponse, trigger, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Composio) -> None:
        with client.org.project.trigger.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trigger = response.parse()
            assert_matches_type(TriggerListResponse, trigger, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTrigger:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_update(self, async_client: AsyncComposio) -> None:
        trigger = await async_client.org.project.trigger.update()
        assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncComposio) -> None:
        trigger = await async_client.org.project.trigger.update(
            enabled=True,
        )
        assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncComposio) -> None:
        response = await async_client.org.project.trigger.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trigger = await response.parse()
        assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncComposio) -> None:
        async with async_client.org.project.trigger.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trigger = await response.parse()
            assert_matches_type(TriggerUpdateResponse, trigger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncComposio) -> None:
        trigger = await async_client.org.project.trigger.list()
        assert_matches_type(TriggerListResponse, trigger, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncComposio) -> None:
        response = await async_client.org.project.trigger.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trigger = await response.parse()
        assert_matches_type(TriggerListResponse, trigger, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncComposio) -> None:
        async with async_client.org.project.trigger.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trigger = await response.parse()
            assert_matches_type(TriggerListResponse, trigger, path=["response"])

        assert cast(Any, response.is_closed) is True
