# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    RoleListResponse,
    RoleCreateResponse,
    RoleUpdateResponse,
    RoleRetrieveResponse,
    UpdateDefaultRolesResponse,
    RoleRetrieveDependentsResponse,
    RoleRetrieveUsersCountResponse,
    RoleRetrievePermissionsAllResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRoles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.create()
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.create(
            description="description",
            display_name="display_name",
            extends="extends",
            name="name",
            permissions=["string"],
        )
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleCreateResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.retrieve(
            role_name="role_name",
        )
        assert_matches_type(RoleRetrieveResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.retrieve(
            role_name="role_name",
            include="include",
        )
        assert_matches_type(RoleRetrieveResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.retrieve(
            role_name="role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleRetrieveResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.retrieve(
            role_name="role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleRetrieveResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.retrieve(
                role_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.update(
            role_name="role_name",
        )
        assert_matches_type(RoleUpdateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.update(
            role_name="role_name",
            description="description",
            display_name="display_name",
            extends="extends",
            permissions=["string"],
        )
        assert_matches_type(RoleUpdateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.update(
            role_name="role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleUpdateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.update(
            role_name="role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleUpdateResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.update(
                role_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.list()
        assert_matches_type(RoleListResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.list(
            include="include",
        )
        assert_matches_type(RoleListResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleListResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleListResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.delete(
            role_name="role_name",
        )
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.delete(
            role_name="role_name",
            reassign_role_id="reassign_role_id",
            reassign_role_name="reassign_role_name",
        )
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.delete(
            role_name="role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.delete(
            role_name="role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert role is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.delete(
                role_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_base(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.delete_base(
            "role_name",
        )
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_base(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.delete_base(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_base(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.delete_base(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert role is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_base(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.delete_base(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_dependents(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.retrieve_dependents(
            "role_name",
        )
        assert_matches_type(RoleRetrieveDependentsResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_dependents(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.retrieve_dependents(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleRetrieveDependentsResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_dependents(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.retrieve_dependents(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleRetrieveDependentsResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_dependents(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.retrieve_dependents(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_permissions_all(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.retrieve_permissions_all(
            "role_name",
        )
        assert_matches_type(RoleRetrievePermissionsAllResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_permissions_all(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.retrieve_permissions_all(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleRetrievePermissionsAllResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_permissions_all(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.retrieve_permissions_all(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleRetrievePermissionsAllResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_permissions_all(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.retrieve_permissions_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_users_count(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.retrieve_users_count(
            "role_name",
        )
        assert_matches_type(RoleRetrieveUsersCountResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_users_count(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.retrieve_users_count(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleRetrieveUsersCountResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_users_count(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.retrieve_users_count(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleRetrieveUsersCountResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_users_count(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            client.api.v1.roles.with_raw_response.retrieve_users_count(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_default(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.update_default()
        assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_default_with_all_params(self, client: ScalekitDemo) -> None:
        role = client.api.v1.roles.update_default(
            default_creator={
                "id": "id",
                "name": "name",
            },
            default_creator_role="default_creator_role",
            default_member={
                "id": "id",
                "name": "name",
            },
            default_member_role="default_member_role",
        )
        assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_default(self, client: ScalekitDemo) -> None:
        response = client.api.v1.roles.with_raw_response.update_default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_default(self, client: ScalekitDemo) -> None:
        with client.api.v1.roles.with_streaming_response.update_default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRoles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.create()
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.create(
            description="description",
            display_name="display_name",
            extends="extends",
            name="name",
            permissions=["string"],
        )
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleCreateResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.retrieve(
            role_name="role_name",
        )
        assert_matches_type(RoleRetrieveResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.retrieve(
            role_name="role_name",
            include="include",
        )
        assert_matches_type(RoleRetrieveResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.retrieve(
            role_name="role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleRetrieveResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.retrieve(
            role_name="role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleRetrieveResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.retrieve(
                role_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.update(
            role_name="role_name",
        )
        assert_matches_type(RoleUpdateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.update(
            role_name="role_name",
            description="description",
            display_name="display_name",
            extends="extends",
            permissions=["string"],
        )
        assert_matches_type(RoleUpdateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.update(
            role_name="role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleUpdateResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.update(
            role_name="role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleUpdateResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.update(
                role_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.list()
        assert_matches_type(RoleListResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.list(
            include="include",
        )
        assert_matches_type(RoleListResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleListResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleListResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.delete(
            role_name="role_name",
        )
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.delete(
            role_name="role_name",
            reassign_role_id="reassign_role_id",
            reassign_role_name="reassign_role_name",
        )
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.delete(
            role_name="role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.delete(
            role_name="role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert role is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.delete(
                role_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_base(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.delete_base(
            "role_name",
        )
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_base(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.delete_base(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert role is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_base(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.delete_base(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert role is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_base(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.delete_base(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_dependents(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.retrieve_dependents(
            "role_name",
        )
        assert_matches_type(RoleRetrieveDependentsResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_dependents(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.retrieve_dependents(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleRetrieveDependentsResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_dependents(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.retrieve_dependents(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleRetrieveDependentsResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_dependents(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.retrieve_dependents(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_permissions_all(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.retrieve_permissions_all(
            "role_name",
        )
        assert_matches_type(RoleRetrievePermissionsAllResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_permissions_all(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.retrieve_permissions_all(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleRetrievePermissionsAllResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_permissions_all(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.retrieve_permissions_all(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleRetrievePermissionsAllResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_permissions_all(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.retrieve_permissions_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_users_count(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.retrieve_users_count(
            "role_name",
        )
        assert_matches_type(RoleRetrieveUsersCountResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_users_count(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.retrieve_users_count(
            "role_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(RoleRetrieveUsersCountResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_users_count(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.retrieve_users_count(
            "role_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleRetrieveUsersCountResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_users_count(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_name` but received ''"):
            await async_client.api.v1.roles.with_raw_response.retrieve_users_count(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_default(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.update_default()
        assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_default_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        role = await async_client.api.v1.roles.update_default(
            default_creator={
                "id": "id",
                "name": "name",
            },
            default_creator_role="default_creator_role",
            default_member={
                "id": "id",
                "name": "name",
            },
            default_member_role="default_member_role",
        )
        assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_default(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.roles.with_raw_response.update_default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = await response.parse()
        assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_default(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.roles.with_streaming_response.update_default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(UpdateDefaultRolesResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True
