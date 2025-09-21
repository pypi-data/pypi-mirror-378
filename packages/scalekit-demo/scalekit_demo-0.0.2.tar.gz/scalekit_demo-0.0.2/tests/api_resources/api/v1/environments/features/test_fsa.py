# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scalekit_demo import ScalekitDemo, AsyncScalekitDemo

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFsa:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_enable(self, client: ScalekitDemo) -> None:
        fsa = client.api.v1.environments.features.fsa.enable(
            path_id="id",
        )
        assert fsa is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_enable_with_all_params(self, client: ScalekitDemo) -> None:
        fsa = client.api.v1.environments.features.fsa.enable(
            path_id="id",
            body_id="id",
        )
        assert fsa is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_enable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.features.fsa.with_raw_response.enable(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fsa = response.parse()
        assert fsa is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_enable(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.features.fsa.with_streaming_response.enable(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fsa = response.parse()
            assert fsa is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_enable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.environments.features.fsa.with_raw_response.enable(
                path_id="",
            )


class TestAsyncFsa:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_enable(self, async_client: AsyncScalekitDemo) -> None:
        fsa = await async_client.api.v1.environments.features.fsa.enable(
            path_id="id",
        )
        assert fsa is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_enable_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        fsa = await async_client.api.v1.environments.features.fsa.enable(
            path_id="id",
            body_id="id",
        )
        assert fsa is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_enable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.features.fsa.with_raw_response.enable(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fsa = await response.parse()
        assert fsa is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_enable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.features.fsa.with_streaming_response.enable(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fsa = await response.parse()
            assert fsa is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_enable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.environments.features.fsa.with_raw_response.enable(
                path_id="",
            )
