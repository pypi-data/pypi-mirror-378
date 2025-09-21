# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.environments import GetCurrentSessionResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessionsMe:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        sessions_me = client.api.v1.environments.sessions_me.retrieve_sessions_me(
            "id",
        )
        assert_matches_type(GetCurrentSessionResponse, sessions_me, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.sessions_me.with_raw_response.retrieve_sessions_me(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sessions_me = response.parse()
        assert_matches_type(GetCurrentSessionResponse, sessions_me, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.sessions_me.with_streaming_response.retrieve_sessions_me(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sessions_me = response.parse()
            assert_matches_type(GetCurrentSessionResponse, sessions_me, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.sessions_me.with_raw_response.retrieve_sessions_me(
                "",
            )


class TestAsyncSessionsMe:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        sessions_me = await async_client.api.v1.environments.sessions_me.retrieve_sessions_me(
            "id",
        )
        assert_matches_type(GetCurrentSessionResponse, sessions_me, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.sessions_me.with_raw_response.retrieve_sessions_me(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sessions_me = await response.parse()
        assert_matches_type(GetCurrentSessionResponse, sessions_me, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.sessions_me.with_streaming_response.retrieve_sessions_me(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sessions_me = await response.parse()
            assert_matches_type(GetCurrentSessionResponse, sessions_me, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.sessions_me.with_raw_response.retrieve_sessions_me(
                "",
            )
