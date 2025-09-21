# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    ConnectedAccountListResponse,
    ConnectedAccountCreateResponse,
    ConnectedAccountRetrieveAuthResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConnectedAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        connected_account = client.api.v1.connected_accounts.create()
        assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        connected_account = client.api.v1.connected_accounts.create(
            connected_account={
                "api_config": {},
                "authorization_details": {
                    "oauth_token": {
                        "access_token": "access_token",
                        "domain": "domain",
                        "refresh_token": "refresh_token",
                        "scopes": ["string"],
                    },
                    "static_auth": {"details": {}},
                },
            },
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connected_accounts.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connected_account = response.parse()
        assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.connected_accounts.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connected_account = response.parse()
            assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        connected_account = client.api.v1.connected_accounts.list()
        assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        connected_account = client.api.v1.connected_accounts.list(
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            page_size=0,
            page_token="page_token",
            provider="provider",
            query="query",
            user_id="user_id",
        )
        assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connected_accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connected_account = response.parse()
        assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.connected_accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connected_account = response.parse()
            assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_auth(self, client: ScalekitDemo) -> None:
        connected_account = client.api.v1.connected_accounts.retrieve_auth()
        assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_auth_with_all_params(self, client: ScalekitDemo) -> None:
        connected_account = client.api.v1.connected_accounts.retrieve_auth(
            id="id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_auth(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connected_accounts.with_raw_response.retrieve_auth()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connected_account = response.parse()
        assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_auth(self, client: ScalekitDemo) -> None:
        with client.api.v1.connected_accounts.with_streaming_response.retrieve_auth() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connected_account = response.parse()
            assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConnectedAccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        connected_account = await async_client.api.v1.connected_accounts.create()
        assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connected_account = await async_client.api.v1.connected_accounts.create(
            connected_account={
                "api_config": {},
                "authorization_details": {
                    "oauth_token": {
                        "access_token": "access_token",
                        "domain": "domain",
                        "refresh_token": "refresh_token",
                        "scopes": ["string"],
                    },
                    "static_auth": {"details": {}},
                },
            },
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connected_accounts.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connected_account = await response.parse()
        assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connected_accounts.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connected_account = await response.parse()
            assert_matches_type(ConnectedAccountCreateResponse, connected_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        connected_account = await async_client.api.v1.connected_accounts.list()
        assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connected_account = await async_client.api.v1.connected_accounts.list(
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            page_size=0,
            page_token="page_token",
            provider="provider",
            query="query",
            user_id="user_id",
        )
        assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connected_accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connected_account = await response.parse()
        assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connected_accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connected_account = await response.parse()
            assert_matches_type(ConnectedAccountListResponse, connected_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_auth(self, async_client: AsyncScalekitDemo) -> None:
        connected_account = await async_client.api.v1.connected_accounts.retrieve_auth()
        assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_auth_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connected_account = await async_client.api.v1.connected_accounts.retrieve_auth(
            id="id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_auth(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connected_accounts.with_raw_response.retrieve_auth()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connected_account = await response.parse()
        assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_auth(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connected_accounts.with_streaming_response.retrieve_auth() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connected_account = await response.parse()
            assert_matches_type(ConnectedAccountRetrieveAuthResponse, connected_account, path=["response"])

        assert cast(Any, response.is_closed) is True
