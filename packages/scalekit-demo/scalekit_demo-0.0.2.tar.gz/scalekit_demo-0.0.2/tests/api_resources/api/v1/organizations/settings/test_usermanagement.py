# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.organizations.settings import (
    UsermanagementListResponse,
    UsermanagementPatchAllResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsermanagement:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        usermanagement = client.api.v1.organizations.settings.usermanagement.list(
            "organization_id",
        )
        assert_matches_type(UsermanagementListResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.settings.usermanagement.with_raw_response.list(
            "organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usermanagement = response.parse()
        assert_matches_type(UsermanagementListResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.settings.usermanagement.with_streaming_response.list(
            "organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usermanagement = response.parse()
            assert_matches_type(UsermanagementListResponse, usermanagement, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.settings.usermanagement.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch_all(self, client: ScalekitDemo) -> None:
        usermanagement = client.api.v1.organizations.settings.usermanagement.patch_all(
            path_organization_id="organization_id",
        )
        assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch_all_with_all_params(self, client: ScalekitDemo) -> None:
        usermanagement = client.api.v1.organizations.settings.usermanagement.patch_all(
            path_organization_id="organization_id",
            body_organization_id="organization_id",
            settings={
                "deprecated_placeholder": 0,
                "jit_provisioning_with_sso_enabled": True,
                "sync_user_profile_on_signin": True,
            },
        )
        assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patch_all(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.settings.usermanagement.with_raw_response.patch_all(
            path_organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usermanagement = response.parse()
        assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patch_all(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.settings.usermanagement.with_streaming_response.patch_all(
            path_organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usermanagement = response.parse()
            assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_patch_all(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_organization_id` but received ''"):
            client.api.v1.organizations.settings.usermanagement.with_raw_response.patch_all(
                path_organization_id="",
            )


class TestAsyncUsermanagement:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        usermanagement = await async_client.api.v1.organizations.settings.usermanagement.list(
            "organization_id",
        )
        assert_matches_type(UsermanagementListResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.settings.usermanagement.with_raw_response.list(
            "organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usermanagement = await response.parse()
        assert_matches_type(UsermanagementListResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.settings.usermanagement.with_streaming_response.list(
            "organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usermanagement = await response.parse()
            assert_matches_type(UsermanagementListResponse, usermanagement, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.settings.usermanagement.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        usermanagement = await async_client.api.v1.organizations.settings.usermanagement.patch_all(
            path_organization_id="organization_id",
        )
        assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch_all_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        usermanagement = await async_client.api.v1.organizations.settings.usermanagement.patch_all(
            path_organization_id="organization_id",
            body_organization_id="organization_id",
            settings={
                "deprecated_placeholder": 0,
                "jit_provisioning_with_sso_enabled": True,
                "sync_user_profile_on_signin": True,
            },
        )
        assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.settings.usermanagement.with_raw_response.patch_all(
            path_organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usermanagement = await response.parse()
        assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.settings.usermanagement.with_streaming_response.patch_all(
            path_organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usermanagement = await response.parse()
            assert_matches_type(UsermanagementPatchAllResponse, usermanagement, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_organization_id` but received ''"):
            await async_client.api.v1.organizations.settings.usermanagement.with_raw_response.patch_all(
                path_organization_id="",
            )
