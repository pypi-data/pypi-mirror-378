# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scalekit_demo import ScalekitDemo, AsyncScalekitDemo

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuthRequests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_user(self, client: ScalekitDemo) -> None:
        auth_request = client.api.v1.connections.auth_requests.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
        )
        assert auth_request is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_user_with_all_params(self, client: ScalekitDemo) -> None:
        auth_request = client.api.v1.connections.auth_requests.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
            custom_attributes={},
            email="email",
            email_verified=True,
            family_name="family_name",
            gender="gender",
            given_name="given_name",
            groups=["string"],
            locale="locale",
            name="name",
            phone_number="phone_number",
            phone_number_verified=True,
            picture="picture",
            preferred_username="preferred_username",
            sub="sub",
        )
        assert auth_request is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_user(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.auth_requests.with_raw_response.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth_request = response.parse()
        assert auth_request is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_user(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.auth_requests.with_streaming_response.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth_request = response.parse()
            assert auth_request is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_user(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.api.v1.connections.auth_requests.with_raw_response.user(
                login_request_id="login_request_id",
                connection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `login_request_id` but received ''"):
            client.api.v1.connections.auth_requests.with_raw_response.user(
                login_request_id="",
                connection_id="connection_id",
            )


class TestAsyncAuthRequests:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_user(self, async_client: AsyncScalekitDemo) -> None:
        auth_request = await async_client.api.v1.connections.auth_requests.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
        )
        assert auth_request is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_user_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        auth_request = await async_client.api.v1.connections.auth_requests.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
            custom_attributes={},
            email="email",
            email_verified=True,
            family_name="family_name",
            gender="gender",
            given_name="given_name",
            groups=["string"],
            locale="locale",
            name="name",
            phone_number="phone_number",
            phone_number_verified=True,
            picture="picture",
            preferred_username="preferred_username",
            sub="sub",
        )
        assert auth_request is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_user(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.auth_requests.with_raw_response.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth_request = await response.parse()
        assert auth_request is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_user(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.auth_requests.with_streaming_response.user(
            login_request_id="login_request_id",
            connection_id="connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth_request = await response.parse()
            assert auth_request is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_user(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.api.v1.connections.auth_requests.with_raw_response.user(
                login_request_id="login_request_id",
                connection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `login_request_id` but received ''"):
            await async_client.api.v1.connections.auth_requests.with_raw_response.user(
                login_request_id="",
                connection_id="connection_id",
            )
