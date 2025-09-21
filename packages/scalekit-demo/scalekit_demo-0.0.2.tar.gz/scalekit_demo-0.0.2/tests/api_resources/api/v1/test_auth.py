# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import AuthRetrieveStateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_logout(self, client: ScalekitDemo) -> None:
        auth = client.api.v1.auth.logout()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_logout(self, client: ScalekitDemo) -> None:
        response = client.api.v1.auth.with_raw_response.logout()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_logout(self, client: ScalekitDemo) -> None:
        with client.api.v1.auth.with_streaming_response.logout() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_passwordless_resend(self, client: ScalekitDemo) -> None:
        auth = client.api.v1.auth.passwordless_resend()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_passwordless_resend(self, client: ScalekitDemo) -> None:
        response = client.api.v1.auth.with_raw_response.passwordless_resend()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_passwordless_resend(self, client: ScalekitDemo) -> None:
        with client.api.v1.auth.with_streaming_response.passwordless_resend() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_passwordless_verify(self, client: ScalekitDemo) -> None:
        auth = client.api.v1.auth.passwordless_verify()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_passwordless_verify_with_all_params(self, client: ScalekitDemo) -> None:
        auth = client.api.v1.auth.passwordless_verify(
            code_challenge="code_challenge",
        )
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_passwordless_verify(self, client: ScalekitDemo) -> None:
        response = client.api.v1.auth.with_raw_response.passwordless_verify()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_passwordless_verify(self, client: ScalekitDemo) -> None:
        with client.api.v1.auth.with_streaming_response.passwordless_verify() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(object, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_state(self, client: ScalekitDemo) -> None:
        auth = client.api.v1.auth.retrieve_state()
        assert_matches_type(AuthRetrieveStateResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_state(self, client: ScalekitDemo) -> None:
        response = client.api.v1.auth.with_raw_response.retrieve_state()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthRetrieveStateResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_state(self, client: ScalekitDemo) -> None:
        with client.api.v1.auth.with_streaming_response.retrieve_state() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthRetrieveStateResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_logout(self, async_client: AsyncScalekitDemo) -> None:
        auth = await async_client.api.v1.auth.logout()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_logout(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.auth.with_raw_response.logout()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_logout(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.auth.with_streaming_response.logout() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_passwordless_resend(self, async_client: AsyncScalekitDemo) -> None:
        auth = await async_client.api.v1.auth.passwordless_resend()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_passwordless_resend(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.auth.with_raw_response.passwordless_resend()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert auth is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_passwordless_resend(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.auth.with_streaming_response.passwordless_resend() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_passwordless_verify(self, async_client: AsyncScalekitDemo) -> None:
        auth = await async_client.api.v1.auth.passwordless_verify()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_passwordless_verify_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        auth = await async_client.api.v1.auth.passwordless_verify(
            code_challenge="code_challenge",
        )
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_passwordless_verify(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.auth.with_raw_response.passwordless_verify()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_passwordless_verify(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.auth.with_streaming_response.passwordless_verify() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(object, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_state(self, async_client: AsyncScalekitDemo) -> None:
        auth = await async_client.api.v1.auth.retrieve_state()
        assert_matches_type(AuthRetrieveStateResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_state(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.auth.with_raw_response.retrieve_state()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthRetrieveStateResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_state(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.auth.with_streaming_response.retrieve_state() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthRetrieveStateResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
