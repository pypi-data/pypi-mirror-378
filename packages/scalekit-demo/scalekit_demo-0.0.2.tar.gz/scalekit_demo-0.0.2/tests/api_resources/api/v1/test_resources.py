# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    GetResourceResponse,
    ResourceListResponse,
    ResourceCreateResponse,
    ResourceUpdateResponse,
    ResourceClientsRegisterResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResources:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.create()
        assert_matches_type(ResourceCreateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.create(
            access_token_expiry="access_token_expiry",
            description="description",
            disable_dynamic_client_registration=True,
            logo_uri="logo_uri",
            name="name",
            provider="provider",
            refresh_token_expiry="refresh_token_expiry",
            resource_id="resource_id",
            resource_type=0,
            resource_uri="resource_uri",
            scopes=["string"],
        )
        assert_matches_type(ResourceCreateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert_matches_type(ResourceCreateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert_matches_type(ResourceCreateResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.retrieve(
            "resource_id",
        )
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.retrieve(
            "resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.retrieve(
            "resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert_matches_type(GetResourceResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.api.v1.resources.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.update(
            path_resource_id="resource_id",
        )
        assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.update(
            path_resource_id="resource_id",
            update_mask="update_mask",
            access_token_expiry="access_token_expiry",
            description="description",
            disable_dynamic_client_registration=True,
            logo_uri="logo_uri",
            name="name",
            provider="provider",
            refresh_token_expiry="refresh_token_expiry",
            body_resource_id="resource_id",
            resource_uri="resource_uri",
            scopes=["string"],
        )
        assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.update(
            path_resource_id="resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.update(
            path_resource_id="resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_resource_id` but received ''"):
            client.api.v1.resources.with_raw_response.update(
                path_resource_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.list()
        assert_matches_type(ResourceListResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.list(
            page_size=0,
            page_token="page_token",
            resource_type=0,
        )
        assert_matches_type(ResourceListResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert_matches_type(ResourceListResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert_matches_type(ResourceListResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.delete(
            "resource_id",
        )
        assert resource is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.delete(
            "resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert resource is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.delete(
            "resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert resource is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.api.v1.resources.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clients_register(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.clients_register(
            res_id="res_id",
        )
        assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clients_register_with_all_params(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.clients_register(
            res_id="res_id",
            client_name="client_name",
            client_uri="client_uri",
            description="description",
            logo_uri="logo_uri",
            policy_uri="policy_uri",
            redirect_uris=["string"],
            scope="scope",
            tos_uri="tos_uri",
        )
        assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clients_register(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.clients_register(
            res_id="res_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clients_register(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.clients_register(
            res_id="res_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clients_register(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `res_id` but received ''"):
            client.api.v1.resources.with_raw_response.clients_register(
                res_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_provider_delete(self, client: ScalekitDemo) -> None:
        resource = client.api.v1.resources.update_provider_delete(
            "resource_id",
        )
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_provider_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.resources.with_raw_response.update_provider_delete(
            "resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = response.parse()
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_provider_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.resources.with_streaming_response.update_provider_delete(
            "resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = response.parse()
            assert_matches_type(GetResourceResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_provider_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.api.v1.resources.with_raw_response.update_provider_delete(
                "",
            )


class TestAsyncResources:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.create()
        assert_matches_type(ResourceCreateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.create(
            access_token_expiry="access_token_expiry",
            description="description",
            disable_dynamic_client_registration=True,
            logo_uri="logo_uri",
            name="name",
            provider="provider",
            refresh_token_expiry="refresh_token_expiry",
            resource_id="resource_id",
            resource_type=0,
            resource_uri="resource_uri",
            scopes=["string"],
        )
        assert_matches_type(ResourceCreateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert_matches_type(ResourceCreateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert_matches_type(ResourceCreateResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.retrieve(
            "resource_id",
        )
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.retrieve(
            "resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.retrieve(
            "resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert_matches_type(GetResourceResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.api.v1.resources.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.update(
            path_resource_id="resource_id",
        )
        assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.update(
            path_resource_id="resource_id",
            update_mask="update_mask",
            access_token_expiry="access_token_expiry",
            description="description",
            disable_dynamic_client_registration=True,
            logo_uri="logo_uri",
            name="name",
            provider="provider",
            refresh_token_expiry="refresh_token_expiry",
            body_resource_id="resource_id",
            resource_uri="resource_uri",
            scopes=["string"],
        )
        assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.update(
            path_resource_id="resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.update(
            path_resource_id="resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert_matches_type(ResourceUpdateResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_resource_id` but received ''"):
            await async_client.api.v1.resources.with_raw_response.update(
                path_resource_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.list()
        assert_matches_type(ResourceListResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.list(
            page_size=0,
            page_token="page_token",
            resource_type=0,
        )
        assert_matches_type(ResourceListResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert_matches_type(ResourceListResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert_matches_type(ResourceListResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.delete(
            "resource_id",
        )
        assert resource is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.delete(
            "resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert resource is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.delete(
            "resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert resource is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.api.v1.resources.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clients_register(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.clients_register(
            res_id="res_id",
        )
        assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clients_register_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.clients_register(
            res_id="res_id",
            client_name="client_name",
            client_uri="client_uri",
            description="description",
            logo_uri="logo_uri",
            policy_uri="policy_uri",
            redirect_uris=["string"],
            scope="scope",
            tos_uri="tos_uri",
        )
        assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clients_register(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.clients_register(
            res_id="res_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clients_register(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.clients_register(
            res_id="res_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert_matches_type(ResourceClientsRegisterResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clients_register(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `res_id` but received ''"):
            await async_client.api.v1.resources.with_raw_response.clients_register(
                res_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_provider_delete(self, async_client: AsyncScalekitDemo) -> None:
        resource = await async_client.api.v1.resources.update_provider_delete(
            "resource_id",
        )
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_provider_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.resources.with_raw_response.update_provider_delete(
            "resource_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource = await response.parse()
        assert_matches_type(GetResourceResponse, resource, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_provider_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.resources.with_streaming_response.update_provider_delete(
            "resource_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource = await response.parse()
            assert_matches_type(GetResourceResponse, resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_provider_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.api.v1.resources.with_raw_response.update_provider_delete(
                "",
            )
