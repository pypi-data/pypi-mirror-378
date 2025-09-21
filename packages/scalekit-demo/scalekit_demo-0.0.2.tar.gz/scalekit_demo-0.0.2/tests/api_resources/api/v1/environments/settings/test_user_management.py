# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.environments.settings import (
    UserManagementUserManagementResponse,
    UserManagementUpdateUserManagementResponse,
    UserManagementRetrieveUserManagementResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUserManagement:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_user_management(self, client: ScalekitDemo) -> None:
        user_management = client.api.v1.environments.settings.user_management.retrieve_user_management(
            "id",
        )
        assert_matches_type(UserManagementRetrieveUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_user_management(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.settings.user_management.with_raw_response.retrieve_user_management(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_management = response.parse()
        assert_matches_type(UserManagementRetrieveUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_user_management(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.settings.user_management.with_streaming_response.retrieve_user_management(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_management = response.parse()
            assert_matches_type(UserManagementRetrieveUserManagementResponse, user_management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_user_management(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.settings.user_management.with_raw_response.retrieve_user_management(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_user_management(self, client: ScalekitDemo) -> None:
        user_management = client.api.v1.environments.settings.user_management.update_user_management(
            id="id",
        )
        assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_user_management_with_all_params(self, client: ScalekitDemo) -> None:
        user_management = client.api.v1.environments.settings.user_management.update_user_management(
            id="id",
            allow_duplicate_user_identities=True,
            allow_multiple_memberships=True,
            allow_organization_signup=True,
            block_disposable_email_domains=True,
            block_public_email_domains=True,
            enable_max_users_limit=True,
            invitation_expiry=0,
            max_users_limit=0,
            org_user_relationship=0,
        )
        assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_user_management(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.settings.user_management.with_raw_response.update_user_management(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_management = response.parse()
        assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_user_management(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.settings.user_management.with_streaming_response.update_user_management(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_management = response.parse()
            assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_user_management(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.settings.user_management.with_raw_response.update_user_management(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_user_management(self, client: ScalekitDemo) -> None:
        user_management = client.api.v1.environments.settings.user_management.user_management(
            id="id",
        )
        assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_user_management_with_all_params(self, client: ScalekitDemo) -> None:
        user_management = client.api.v1.environments.settings.user_management.user_management(
            id="id",
            allow_duplicate_user_identities=True,
            allow_multiple_memberships=True,
            allow_organization_signup=True,
            block_disposable_email_domains=True,
            block_public_email_domains=True,
            enable_max_users_limit=True,
            invitation_expiry=0,
            max_users_limit=0,
            org_user_relationship=0,
        )
        assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_user_management(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.settings.user_management.with_raw_response.user_management(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_management = response.parse()
        assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_user_management(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.settings.user_management.with_streaming_response.user_management(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_management = response.parse()
            assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_user_management(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.settings.user_management.with_raw_response.user_management(
                id="",
            )


class TestAsyncUserManagement:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_user_management(self, async_client: AsyncScalekitDemo) -> None:
        user_management = await async_client.api.v1.environments.settings.user_management.retrieve_user_management(
            "id",
        )
        assert_matches_type(UserManagementRetrieveUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_user_management(self, async_client: AsyncScalekitDemo) -> None:
        response = (
            await async_client.api.v1.environments.settings.user_management.with_raw_response.retrieve_user_management(
                "id",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_management = await response.parse()
        assert_matches_type(UserManagementRetrieveUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_user_management(self, async_client: AsyncScalekitDemo) -> None:
        async with (
            async_client.api.v1.environments.settings.user_management.with_streaming_response.retrieve_user_management(
                "id",
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_management = await response.parse()
            assert_matches_type(UserManagementRetrieveUserManagementResponse, user_management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_user_management(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.settings.user_management.with_raw_response.retrieve_user_management(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_user_management(self, async_client: AsyncScalekitDemo) -> None:
        user_management = await async_client.api.v1.environments.settings.user_management.update_user_management(
            id="id",
        )
        assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_user_management_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user_management = await async_client.api.v1.environments.settings.user_management.update_user_management(
            id="id",
            allow_duplicate_user_identities=True,
            allow_multiple_memberships=True,
            allow_organization_signup=True,
            block_disposable_email_domains=True,
            block_public_email_domains=True,
            enable_max_users_limit=True,
            invitation_expiry=0,
            max_users_limit=0,
            org_user_relationship=0,
        )
        assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_user_management(self, async_client: AsyncScalekitDemo) -> None:
        response = (
            await async_client.api.v1.environments.settings.user_management.with_raw_response.update_user_management(
                id="id",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_management = await response.parse()
        assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_user_management(self, async_client: AsyncScalekitDemo) -> None:
        async with (
            async_client.api.v1.environments.settings.user_management.with_streaming_response.update_user_management(
                id="id",
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_management = await response.parse()
            assert_matches_type(UserManagementUpdateUserManagementResponse, user_management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_user_management(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.settings.user_management.with_raw_response.update_user_management(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_user_management(self, async_client: AsyncScalekitDemo) -> None:
        user_management = await async_client.api.v1.environments.settings.user_management.user_management(
            id="id",
        )
        assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_user_management_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user_management = await async_client.api.v1.environments.settings.user_management.user_management(
            id="id",
            allow_duplicate_user_identities=True,
            allow_multiple_memberships=True,
            allow_organization_signup=True,
            block_disposable_email_domains=True,
            block_public_email_domains=True,
            enable_max_users_limit=True,
            invitation_expiry=0,
            max_users_limit=0,
            org_user_relationship=0,
        )
        assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_user_management(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.settings.user_management.with_raw_response.user_management(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_management = await response.parse()
        assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_user_management(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.settings.user_management.with_streaming_response.user_management(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_management = await response.parse()
            assert_matches_type(UserManagementUserManagementResponse, user_management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_user_management(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.settings.user_management.with_raw_response.user_management(
                id="",
            )
