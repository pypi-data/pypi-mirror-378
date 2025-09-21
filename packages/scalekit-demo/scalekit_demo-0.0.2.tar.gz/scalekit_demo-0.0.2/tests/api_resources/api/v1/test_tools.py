# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    ToolListResponse,
    ToolCreateResponse,
    ToolRetrieveScopedResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTools:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.create()
        assert_matches_type(ToolCreateResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.create(
            definition={},
            metadata={},
            tags=["string"],
        )
        assert_matches_type(ToolCreateResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.tools.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = response.parse()
        assert_matches_type(ToolCreateResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.tools.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = response.parse()
            assert_matches_type(ToolCreateResponse, tool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.list()
        assert_matches_type(ToolListResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.list(
            filter={
                "identifier": "identifier",
                "provider": "provider",
                "query": "query",
                "summary": True,
                "tool_name": ["string"],
            },
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(ToolListResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.tools.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = response.parse()
        assert_matches_type(ToolListResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.tools.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = response.parse()
            assert_matches_type(ToolListResponse, tool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.delete(
            "id",
        )
        assert tool is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.tools.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = response.parse()
        assert tool is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.tools.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = response.parse()
            assert tool is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.tools.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_scoped(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.retrieve_scoped()
        assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_scoped_with_all_params(self, client: ScalekitDemo) -> None:
        tool = client.api.v1.tools.retrieve_scoped(
            filter={
                "connection_names": ["string"],
                "providers": ["string"],
                "tool_names": ["string"],
            },
            identifier="identifier",
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_scoped(self, client: ScalekitDemo) -> None:
        response = client.api.v1.tools.with_raw_response.retrieve_scoped()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = response.parse()
        assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_scoped(self, client: ScalekitDemo) -> None:
        with client.api.v1.tools.with_streaming_response.retrieve_scoped() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = response.parse()
            assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTools:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.create()
        assert_matches_type(ToolCreateResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.create(
            definition={},
            metadata={},
            tags=["string"],
        )
        assert_matches_type(ToolCreateResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.tools.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = await response.parse()
        assert_matches_type(ToolCreateResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.tools.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = await response.parse()
            assert_matches_type(ToolCreateResponse, tool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.list()
        assert_matches_type(ToolListResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.list(
            filter={
                "identifier": "identifier",
                "provider": "provider",
                "query": "query",
                "summary": True,
                "tool_name": ["string"],
            },
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(ToolListResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.tools.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = await response.parse()
        assert_matches_type(ToolListResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.tools.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = await response.parse()
            assert_matches_type(ToolListResponse, tool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.delete(
            "id",
        )
        assert tool is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.tools.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = await response.parse()
        assert tool is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.tools.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = await response.parse()
            assert tool is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.tools.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_scoped(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.retrieve_scoped()
        assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_scoped_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        tool = await async_client.api.v1.tools.retrieve_scoped(
            filter={
                "connection_names": ["string"],
                "providers": ["string"],
                "tool_names": ["string"],
            },
            identifier="identifier",
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_scoped(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.tools.with_raw_response.retrieve_scoped()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tool = await response.parse()
        assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_scoped(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.tools.with_streaming_response.retrieve_scoped() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tool = await response.parse()
            assert_matches_type(ToolRetrieveScopedResponse, tool, path=["response"])

        assert cast(Any, response.is_closed) is True
