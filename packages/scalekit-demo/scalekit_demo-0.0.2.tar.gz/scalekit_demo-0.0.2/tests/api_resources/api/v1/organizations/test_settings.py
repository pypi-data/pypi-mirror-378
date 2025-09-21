# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import GetOrganizationResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSettings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch_all(self, client: ScalekitDemo) -> None:
        setting = client.api.v1.organizations.settings.patch_all(
            id="id",
        )
        assert_matches_type(GetOrganizationResponse, setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch_all_with_all_params(self, client: ScalekitDemo) -> None:
        setting = client.api.v1.organizations.settings.patch_all(
            id="id",
            features=[
                {
                    "enabled": True,
                    "name": "name",
                }
            ],
        )
        assert_matches_type(GetOrganizationResponse, setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patch_all(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.settings.with_raw_response.patch_all(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        setting = response.parse()
        assert_matches_type(GetOrganizationResponse, setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patch_all(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.settings.with_streaming_response.patch_all(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            setting = response.parse()
            assert_matches_type(GetOrganizationResponse, setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_patch_all(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.settings.with_raw_response.patch_all(
                id="",
            )


class TestAsyncSettings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        setting = await async_client.api.v1.organizations.settings.patch_all(
            id="id",
        )
        assert_matches_type(GetOrganizationResponse, setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch_all_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        setting = await async_client.api.v1.organizations.settings.patch_all(
            id="id",
            features=[
                {
                    "enabled": True,
                    "name": "name",
                }
            ],
        )
        assert_matches_type(GetOrganizationResponse, setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.settings.with_raw_response.patch_all(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        setting = await response.parse()
        assert_matches_type(GetOrganizationResponse, setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.settings.with_streaming_response.patch_all(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            setting = await response.parse()
            assert_matches_type(GetOrganizationResponse, setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_patch_all(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.settings.with_raw_response.patch_all(
                id="",
            )
