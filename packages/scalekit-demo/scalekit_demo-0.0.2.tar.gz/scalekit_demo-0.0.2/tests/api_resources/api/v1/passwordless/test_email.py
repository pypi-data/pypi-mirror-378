# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.passwordless import (
    SendPasswordlessResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEmail:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resend(self, client: ScalekitDemo) -> None:
        email = client.api.v1.passwordless.email.resend()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resend_with_all_params(self, client: ScalekitDemo) -> None:
        email = client.api.v1.passwordless.email.resend(
            auth_request_id="auth_request_id",
        )
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_resend(self, client: ScalekitDemo) -> None:
        response = client.api.v1.passwordless.email.with_raw_response.resend()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        email = response.parse()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_resend(self, client: ScalekitDemo) -> None:
        with client.api.v1.passwordless.email.with_streaming_response.resend() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            email = response.parse()
            assert_matches_type(SendPasswordlessResponse, email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send(self, client: ScalekitDemo) -> None:
        email = client.api.v1.passwordless.email.send()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_with_all_params(self, client: ScalekitDemo) -> None:
        email = client.api.v1.passwordless.email.send(
            email="email",
            expires_in=0,
            magiclink_auth_uri="magiclink_auth_uri",
            state="state",
            template=0,
            template_variables={"foo": "string"},
        )
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send(self, client: ScalekitDemo) -> None:
        response = client.api.v1.passwordless.email.with_raw_response.send()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        email = response.parse()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send(self, client: ScalekitDemo) -> None:
        with client.api.v1.passwordless.email.with_streaming_response.send() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            email = response.parse()
            assert_matches_type(SendPasswordlessResponse, email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_verify(self, client: ScalekitDemo) -> None:
        email = client.api.v1.passwordless.email.verify()
        assert_matches_type(object, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_verify_with_all_params(self, client: ScalekitDemo) -> None:
        email = client.api.v1.passwordless.email.verify(
            otp_req={"code_challenge": "code_challenge"},
        )
        assert_matches_type(object, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_verify(self, client: ScalekitDemo) -> None:
        response = client.api.v1.passwordless.email.with_raw_response.verify()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        email = response.parse()
        assert_matches_type(object, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_verify(self, client: ScalekitDemo) -> None:
        with client.api.v1.passwordless.email.with_streaming_response.verify() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            email = response.parse()
            assert_matches_type(object, email, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEmail:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resend(self, async_client: AsyncScalekitDemo) -> None:
        email = await async_client.api.v1.passwordless.email.resend()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resend_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        email = await async_client.api.v1.passwordless.email.resend(
            auth_request_id="auth_request_id",
        )
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_resend(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.passwordless.email.with_raw_response.resend()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        email = await response.parse()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_resend(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.passwordless.email.with_streaming_response.resend() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            email = await response.parse()
            assert_matches_type(SendPasswordlessResponse, email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send(self, async_client: AsyncScalekitDemo) -> None:
        email = await async_client.api.v1.passwordless.email.send()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        email = await async_client.api.v1.passwordless.email.send(
            email="email",
            expires_in=0,
            magiclink_auth_uri="magiclink_auth_uri",
            state="state",
            template=0,
            template_variables={"foo": "string"},
        )
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.passwordless.email.with_raw_response.send()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        email = await response.parse()
        assert_matches_type(SendPasswordlessResponse, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.passwordless.email.with_streaming_response.send() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            email = await response.parse()
            assert_matches_type(SendPasswordlessResponse, email, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_verify(self, async_client: AsyncScalekitDemo) -> None:
        email = await async_client.api.v1.passwordless.email.verify()
        assert_matches_type(object, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_verify_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        email = await async_client.api.v1.passwordless.email.verify(
            otp_req={"code_challenge": "code_challenge"},
        )
        assert_matches_type(object, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_verify(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.passwordless.email.with_raw_response.verify()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        email = await response.parse()
        assert_matches_type(object, email, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_verify(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.passwordless.email.with_streaming_response.verify() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            email = await response.parse()
            assert_matches_type(object, email, path=["response"])

        assert cast(Any, response.is_closed) is True
