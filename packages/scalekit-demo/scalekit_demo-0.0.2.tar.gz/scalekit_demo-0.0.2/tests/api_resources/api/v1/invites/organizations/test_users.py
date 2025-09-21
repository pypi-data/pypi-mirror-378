# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.invites.organizations import UserUpdateResendResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_resend(self, client: ScalekitDemo) -> None:
        user = client.api.v1.invites.organizations.users.update_resend(
            path_id="id",
            path_organization_id="organization_id",
        )
        assert_matches_type(UserUpdateResendResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_resend_with_all_params(self, client: ScalekitDemo) -> None:
        user = client.api.v1.invites.organizations.users.update_resend(
            path_id="id",
            path_organization_id="organization_id",
            body_id="id",
            body_organization_id="organization_id",
        )
        assert_matches_type(UserUpdateResendResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_resend(self, client: ScalekitDemo) -> None:
        response = client.api.v1.invites.organizations.users.with_raw_response.update_resend(
            path_id="id",
            path_organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserUpdateResendResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_resend(self, client: ScalekitDemo) -> None:
        with client.api.v1.invites.organizations.users.with_streaming_response.update_resend(
            path_id="id",
            path_organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserUpdateResendResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_resend(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_organization_id` but received ''"):
            client.api.v1.invites.organizations.users.with_raw_response.update_resend(
                path_id="id",
                path_organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.invites.organizations.users.with_raw_response.update_resend(
                path_id="",
                path_organization_id="organization_id",
            )


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_resend(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.invites.organizations.users.update_resend(
            path_id="id",
            path_organization_id="organization_id",
        )
        assert_matches_type(UserUpdateResendResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_resend_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        user = await async_client.api.v1.invites.organizations.users.update_resend(
            path_id="id",
            path_organization_id="organization_id",
            body_id="id",
            body_organization_id="organization_id",
        )
        assert_matches_type(UserUpdateResendResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_resend(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.invites.organizations.users.with_raw_response.update_resend(
            path_id="id",
            path_organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserUpdateResendResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_resend(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.invites.organizations.users.with_streaming_response.update_resend(
            path_id="id",
            path_organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserUpdateResendResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_resend(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_organization_id` but received ''"):
            await async_client.api.v1.invites.organizations.users.with_raw_response.update_resend(
                path_id="id",
                path_organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.invites.organizations.users.with_raw_response.update_resend(
                path_id="",
                path_organization_id="organization_id",
            )
