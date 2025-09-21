# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo._utils import parse_datetime
from scalekit_demo.types.api.v1.organizations import (
    UserListResponse,
    UserCreateResponse,
    UserRetrievePermissionsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        user = client.api.v1.organizations.users.create(
            organization_id="organization_id",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        user = client.api.v1.organizations.users.create(
            organization_id="organization_id",
            send_invitation_email=True,
            email="email",
            external_id="external_id",
            membership={
                "inviter_email": "inviter_email",
                "metadata": {"foo": "string"},
                "roles": [
                    {
                        "default_creator": True,
                        "default_member": True,
                        "dependent_roles_count": 0,
                        "description": "description",
                        "display_name": "display_name",
                        "extends": "extends",
                        "is_org_role": True,
                        "name": "name",
                        "permissions": [
                            {
                                "id": "id",
                                "create_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                                "description": "description",
                                "name": "name",
                                "role_name": "role_name",
                                "update_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                            }
                        ],
                    }
                ],
            },
            metadata={"foo": "string"},
            user_profile={
                "custom_attributes": {"foo": "string"},
                "first_name": "first_name",
                "last_name": "last_name",
                "locale": "locale",
                "metadata": {"foo": "string"},
                "name": "name",
                "phone_number": "phone_number",
            },
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.users.with_raw_response.create(
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.users.with_streaming_response.create(
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserCreateResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.users.with_raw_response.create(
                organization_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        user = client.api.v1.organizations.users.list(
            organization_id="organization_id",
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        user = client.api.v1.organizations.users.list(
            organization_id="organization_id",
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.users.with_raw_response.list(
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.users.with_streaming_response.list(
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.users.with_raw_response.list(
                organization_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_permissions(self, client: ScalekitDemo) -> None:
        user = client.api.v1.organizations.users.retrieve_permissions(
            user_id="user_id",
            organization_id="organization_id",
        )
        assert_matches_type(UserRetrievePermissionsResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_permissions(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.users.with_raw_response.retrieve_permissions(
            user_id="user_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserRetrievePermissionsResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_permissions(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.users.with_streaming_response.retrieve_permissions(
            user_id="user_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserRetrievePermissionsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_permissions(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.users.with_raw_response.retrieve_permissions(
                user_id="user_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.api.v1.organizations.users.with_raw_response.retrieve_permissions(
                user_id="",
                organization_id="organization_id",
            )


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.organizations.users.create(
            organization_id="organization_id",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.organizations.users.create(
            organization_id="organization_id",
            send_invitation_email=True,
            email="email",
            external_id="external_id",
            membership={
                "inviter_email": "inviter_email",
                "metadata": {"foo": "string"},
                "roles": [
                    {
                        "default_creator": True,
                        "default_member": True,
                        "dependent_roles_count": 0,
                        "description": "description",
                        "display_name": "display_name",
                        "extends": "extends",
                        "is_org_role": True,
                        "name": "name",
                        "permissions": [
                            {
                                "id": "id",
                                "create_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                                "description": "description",
                                "name": "name",
                                "role_name": "role_name",
                                "update_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                            }
                        ],
                    }
                ],
            },
            metadata={"foo": "string"},
            user_profile={
                "custom_attributes": {"foo": "string"},
                "first_name": "first_name",
                "last_name": "last_name",
                "locale": "locale",
                "metadata": {"foo": "string"},
                "name": "name",
                "phone_number": "phone_number",
            },
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.users.with_raw_response.create(
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.users.with_streaming_response.create(
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserCreateResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.users.with_raw_response.create(
                organization_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.organizations.users.list(
            organization_id="organization_id",
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.organizations.users.list(
            organization_id="organization_id",
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.users.with_raw_response.list(
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.users.with_streaming_response.list(
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.users.with_raw_response.list(
                organization_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_permissions(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.organizations.users.retrieve_permissions(
            user_id="user_id",
            organization_id="organization_id",
        )
        assert_matches_type(UserRetrievePermissionsResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_permissions(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.users.with_raw_response.retrieve_permissions(
            user_id="user_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserRetrievePermissionsResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_permissions(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.users.with_streaming_response.retrieve_permissions(
            user_id="user_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserRetrievePermissionsResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_permissions(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.users.with_raw_response.retrieve_permissions(
                user_id="user_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.api.v1.organizations.users.with_raw_response.retrieve_permissions(
                user_id="",
                organization_id="organization_id",
            )
