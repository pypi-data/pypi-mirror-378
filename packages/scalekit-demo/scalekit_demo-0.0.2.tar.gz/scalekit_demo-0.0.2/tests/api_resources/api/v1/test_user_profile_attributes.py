# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    ListUserAttributesResponse,
    CreateUserAttributeResponse,
    UpdateUserAttributeResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUserProfileAttributes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: ScalekitDemo) -> None:
        user_profile_attribute = client.api.v1.user_profile_attributes.update(
            path_key="key",
        )
        assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: ScalekitDemo) -> None:
        user_profile_attribute = client.api.v1.user_profile_attributes.update(
            path_key="key",
            datatype=0,
            directory_user_additional_info={},
            enabled=True,
            body_key="key",
            label="label",
            required=True,
            sso_addition_info={
                "default_oidc_mapping": "default_oidc_mapping",
                "default_saml_mapping": "default_saml_mapping",
            },
        )
        assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.user_profile_attributes.with_raw_response.update(
            path_key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = response.parse()
        assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.user_profile_attributes.with_streaming_response.update(
            path_key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = response.parse()
            assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_key` but received ''"):
            client.api.v1.user_profile_attributes.with_raw_response.update(
                path_key="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        user_profile_attribute = client.api.v1.user_profile_attributes.delete(
            "key",
        )
        assert user_profile_attribute is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.user_profile_attributes.with_raw_response.delete(
            "key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = response.parse()
        assert user_profile_attribute is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.user_profile_attributes.with_streaming_response.delete(
            "key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = response.parse()
            assert user_profile_attribute is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key` but received ''"):
            client.api.v1.user_profile_attributes.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_user_profile_attributes(self, client: ScalekitDemo) -> None:
        user_profile_attribute = client.api.v1.user_profile_attributes.retrieve_user_profile_attributes()
        assert_matches_type(ListUserAttributesResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_user_profile_attributes(self, client: ScalekitDemo) -> None:
        response = client.api.v1.user_profile_attributes.with_raw_response.retrieve_user_profile_attributes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = response.parse()
        assert_matches_type(ListUserAttributesResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_user_profile_attributes(self, client: ScalekitDemo) -> None:
        with (
            client.api.v1.user_profile_attributes.with_streaming_response.retrieve_user_profile_attributes()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = response.parse()
            assert_matches_type(ListUserAttributesResponse, user_profile_attribute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_user_profile_attributes(self, client: ScalekitDemo) -> None:
        user_profile_attribute = client.api.v1.user_profile_attributes.user_profile_attributes()
        assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_user_profile_attributes_with_all_params(self, client: ScalekitDemo) -> None:
        user_profile_attribute = client.api.v1.user_profile_attributes.user_profile_attributes(
            datatype=0,
            directory_user_additional_info={},
            enabled=True,
            key="key",
            label="label",
            required=True,
            sso_addition_info={
                "default_oidc_mapping": "default_oidc_mapping",
                "default_saml_mapping": "default_saml_mapping",
            },
        )
        assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_user_profile_attributes(self, client: ScalekitDemo) -> None:
        response = client.api.v1.user_profile_attributes.with_raw_response.user_profile_attributes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = response.parse()
        assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_user_profile_attributes(self, client: ScalekitDemo) -> None:
        with client.api.v1.user_profile_attributes.with_streaming_response.user_profile_attributes() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = response.parse()
            assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUserProfileAttributes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncScalekitDemo) -> None:
        user_profile_attribute = await async_client.api.v1.user_profile_attributes.update(
            path_key="key",
        )
        assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user_profile_attribute = await async_client.api.v1.user_profile_attributes.update(
            path_key="key",
            datatype=0,
            directory_user_additional_info={},
            enabled=True,
            body_key="key",
            label="label",
            required=True,
            sso_addition_info={
                "default_oidc_mapping": "default_oidc_mapping",
                "default_saml_mapping": "default_saml_mapping",
            },
        )
        assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.user_profile_attributes.with_raw_response.update(
            path_key="key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = await response.parse()
        assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.user_profile_attributes.with_streaming_response.update(
            path_key="key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = await response.parse()
            assert_matches_type(UpdateUserAttributeResponse, user_profile_attribute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_key` but received ''"):
            await async_client.api.v1.user_profile_attributes.with_raw_response.update(
                path_key="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        user_profile_attribute = await async_client.api.v1.user_profile_attributes.delete(
            "key",
        )
        assert user_profile_attribute is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.user_profile_attributes.with_raw_response.delete(
            "key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = await response.parse()
        assert user_profile_attribute is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.user_profile_attributes.with_streaming_response.delete(
            "key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = await response.parse()
            assert user_profile_attribute is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key` but received ''"):
            await async_client.api.v1.user_profile_attributes.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_user_profile_attributes(self, async_client: AsyncScalekitDemo) -> None:
        user_profile_attribute = await async_client.api.v1.user_profile_attributes.retrieve_user_profile_attributes()
        assert_matches_type(ListUserAttributesResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_user_profile_attributes(self, async_client: AsyncScalekitDemo) -> None:
        response = (
            await async_client.api.v1.user_profile_attributes.with_raw_response.retrieve_user_profile_attributes()
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = await response.parse()
        assert_matches_type(ListUserAttributesResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_user_profile_attributes(self, async_client: AsyncScalekitDemo) -> None:
        async with (
            async_client.api.v1.user_profile_attributes.with_streaming_response.retrieve_user_profile_attributes()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = await response.parse()
            assert_matches_type(ListUserAttributesResponse, user_profile_attribute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_user_profile_attributes(self, async_client: AsyncScalekitDemo) -> None:
        user_profile_attribute = await async_client.api.v1.user_profile_attributes.user_profile_attributes()
        assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_user_profile_attributes_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user_profile_attribute = await async_client.api.v1.user_profile_attributes.user_profile_attributes(
            datatype=0,
            directory_user_additional_info={},
            enabled=True,
            key="key",
            label="label",
            required=True,
            sso_addition_info={
                "default_oidc_mapping": "default_oidc_mapping",
                "default_saml_mapping": "default_saml_mapping",
            },
        )
        assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_user_profile_attributes(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.user_profile_attributes.with_raw_response.user_profile_attributes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_profile_attribute = await response.parse()
        assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_user_profile_attributes(self, async_client: AsyncScalekitDemo) -> None:
        async with (
            async_client.api.v1.user_profile_attributes.with_streaming_response.user_profile_attributes()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_profile_attribute = await response.parse()
            assert_matches_type(CreateUserAttributeResponse, user_profile_attribute, path=["response"])

        assert cast(Any, response.is_closed) is True
