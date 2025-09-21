# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.connected_accounts import (
    MagicLinkCreateResponse,
    MagicLinkRedirectResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMagicLink:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        magic_link = client.api.v1.connected_accounts.magic_link.create()
        assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        magic_link = client.api.v1.connected_accounts.magic_link.create(
            id="id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connected_accounts.magic_link.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        magic_link = response.parse()
        assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.connected_accounts.magic_link.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            magic_link = response.parse()
            assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_redirect(self, client: ScalekitDemo) -> None:
        magic_link = client.api.v1.connected_accounts.magic_link.redirect()
        assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_redirect_with_all_params(self, client: ScalekitDemo) -> None:
        magic_link = client.api.v1.connected_accounts.magic_link.redirect(
            redirect_to="redirect_to",
        )
        assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_redirect(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connected_accounts.magic_link.with_raw_response.redirect()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        magic_link = response.parse()
        assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_redirect(self, client: ScalekitDemo) -> None:
        with client.api.v1.connected_accounts.magic_link.with_streaming_response.redirect() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            magic_link = response.parse()
            assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMagicLink:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        magic_link = await async_client.api.v1.connected_accounts.magic_link.create()
        assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        magic_link = await async_client.api.v1.connected_accounts.magic_link.create(
            id="id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connected_accounts.magic_link.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        magic_link = await response.parse()
        assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connected_accounts.magic_link.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            magic_link = await response.parse()
            assert_matches_type(MagicLinkCreateResponse, magic_link, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_redirect(self, async_client: AsyncScalekitDemo) -> None:
        magic_link = await async_client.api.v1.connected_accounts.magic_link.redirect()
        assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_redirect_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        magic_link = await async_client.api.v1.connected_accounts.magic_link.redirect(
            redirect_to="redirect_to",
        )
        assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_redirect(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connected_accounts.magic_link.with_raw_response.redirect()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        magic_link = await response.parse()
        assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_redirect(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connected_accounts.magic_link.with_streaming_response.redirect() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            magic_link = await response.parse()
            assert_matches_type(MagicLinkRedirectResponse, magic_link, path=["response"])

        assert cast(Any, response.is_closed) is True
