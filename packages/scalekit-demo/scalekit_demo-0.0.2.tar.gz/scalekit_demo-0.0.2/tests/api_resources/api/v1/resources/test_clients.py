# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.resources import ClientCreateResponse, ClientRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        client_ = client.api.v1.resources.clients.create(
            resource_id="resource_id",
        )
        assert_matches_type(ClientCreateResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        client_ = client.api.v1.resources.clients.create(
            resource_id="resource_id",
            audience=["string"],
            custom_claims=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            description="description",
            expiry="expiry",
            name="name",
            redirect_uri="redirect_uri",
            scopes=["string"],
        )
        assert_matches_type(ClientCreateResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.clients.with_raw_response.create(
            resource_id="resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(ClientCreateResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.clients.with_streaming_response.create(
            resource_id="resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(ClientCreateResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.api.v1.resources.clients.with_raw_response.create(
                resource_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        client_ = client.api.v1.resources.clients.retrieve(
            client_id="client_id",
            resource_id="resource_id",
        )
        assert_matches_type(ClientRetrieveResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.clients.with_raw_response.retrieve(
            client_id="client_id",
            resource_id="resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(ClientRetrieveResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.clients.with_streaming_response.retrieve(
            client_id="client_id",
            resource_id="resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(ClientRetrieveResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.api.v1.resources.clients.with_raw_response.retrieve(
                client_id="client_id",
                resource_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `client_id` but received ''"):
            client.api.v1.resources.clients.with_raw_response.retrieve(
                client_id="",
                resource_id="resource_id",
            )


class TestAsyncClients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        client = await async_client.api.v1.resources.clients.create(
            resource_id="resource_id",
        )
        assert_matches_type(ClientCreateResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        client = await async_client.api.v1.resources.clients.create(
            resource_id="resource_id",
            audience=["string"],
            custom_claims=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            description="description",
            expiry="expiry",
            name="name",
            redirect_uri="redirect_uri",
            scopes=["string"],
        )
        assert_matches_type(ClientCreateResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.clients.with_raw_response.create(
            resource_id="resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(ClientCreateResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.clients.with_streaming_response.create(
            resource_id="resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(ClientCreateResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.api.v1.resources.clients.with_raw_response.create(
                resource_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        client = await async_client.api.v1.resources.clients.retrieve(
            client_id="client_id",
            resource_id="resource_id",
        )
        assert_matches_type(ClientRetrieveResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.clients.with_raw_response.retrieve(
            client_id="client_id",
            resource_id="resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(ClientRetrieveResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.clients.with_streaming_response.retrieve(
            client_id="client_id",
            resource_id="resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(ClientRetrieveResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.api.v1.resources.clients.with_raw_response.retrieve(
                client_id="client_id",
                resource_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `client_id` but received ''"):
            await async_client.api.v1.resources.clients.with_raw_response.retrieve(
                client_id="",
                resource_id="resource_id",
            )
