# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo._utils import parse_datetime
from scalekit_demo.types.api.v1.organizations.directories import (
    ListDirectoryGroupsResponse,
    GroupUpdateRolesAssignResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGroups:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        group = client.api.v1.organizations.directories.groups.list(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        group = client.api.v1.organizations.directories.groups.list(
            directory_id="directory_id",
            organization_id="organization_id",
            include_detail=True,
            include_external_groups=True,
            page_size=0,
            page_token="page_token",
            updated_after=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.groups.with_raw_response.list(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.groups.with_streaming_response.list(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = response.parse()
            assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.groups.with_raw_response.list(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            client.api.v1.organizations.directories.groups.with_raw_response.list(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_summary(self, client: ScalekitDemo) -> None:
        group = client.api.v1.organizations.directories.groups.retrieve_summary(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_summary(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.groups.with_raw_response.retrieve_summary(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_summary(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.groups.with_streaming_response.retrieve_summary(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = response.parse()
            assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_summary(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.groups.with_raw_response.retrieve_summary(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            client.api.v1.organizations.directories.groups.with_raw_response.retrieve_summary(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_roles_assign(self, client: ScalekitDemo) -> None:
        group = client.api.v1.organizations.directories.groups.update_roles_assign(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_roles_assign_with_all_params(self, client: ScalekitDemo) -> None:
        group = client.api.v1.organizations.directories.groups.update_roles_assign(
            id="id",
            organization_id="organization_id",
            assignments=[
                {
                    "group_id": "group_id",
                    "role_id": "role_id",
                    "role_name": "role_name",
                }
            ],
        )
        assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_roles_assign(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.groups.with_raw_response.update_roles_assign(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_roles_assign(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.groups.with_streaming_response.update_roles_assign(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = response.parse()
            assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_roles_assign(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.groups.with_raw_response.update_roles_assign(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.groups.with_raw_response.update_roles_assign(
                id="",
                organization_id="organization_id",
            )


class TestAsyncGroups:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        group = await async_client.api.v1.organizations.directories.groups.list(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        group = await async_client.api.v1.organizations.directories.groups.list(
            directory_id="directory_id",
            organization_id="organization_id",
            include_detail=True,
            include_external_groups=True,
            page_size=0,
            page_token="page_token",
            updated_after=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.groups.with_raw_response.list(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = await response.parse()
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.groups.with_streaming_response.list(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = await response.parse()
            assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.groups.with_raw_response.list(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            await async_client.api.v1.organizations.directories.groups.with_raw_response.list(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_summary(self, async_client: AsyncScalekitDemo) -> None:
        group = await async_client.api.v1.organizations.directories.groups.retrieve_summary(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_summary(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.groups.with_raw_response.retrieve_summary(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = await response.parse()
        assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_summary(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.groups.with_streaming_response.retrieve_summary(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = await response.parse()
            assert_matches_type(ListDirectoryGroupsResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_summary(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.groups.with_raw_response.retrieve_summary(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            await async_client.api.v1.organizations.directories.groups.with_raw_response.retrieve_summary(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_roles_assign(self, async_client: AsyncScalekitDemo) -> None:
        group = await async_client.api.v1.organizations.directories.groups.update_roles_assign(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_roles_assign_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        group = await async_client.api.v1.organizations.directories.groups.update_roles_assign(
            id="id",
            organization_id="organization_id",
            assignments=[
                {
                    "group_id": "group_id",
                    "role_id": "role_id",
                    "role_name": "role_name",
                }
            ],
        )
        assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_roles_assign(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.groups.with_raw_response.update_roles_assign(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = await response.parse()
        assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_roles_assign(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.groups.with_streaming_response.update_roles_assign(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = await response.parse()
            assert_matches_type(GroupUpdateRolesAssignResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_roles_assign(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.groups.with_raw_response.update_roles_assign(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.groups.with_raw_response.update_roles_assign(
                id="",
                organization_id="organization_id",
            )
