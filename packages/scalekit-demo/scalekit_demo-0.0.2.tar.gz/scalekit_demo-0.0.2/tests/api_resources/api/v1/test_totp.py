# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo._utils import parse_datetime
from scalekit_demo.types.api.v1 import (
    TotpEnableResponse,
    VerifyCodeResponse,
    TotpRegistrationResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTotp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_disable(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.disable(
            path_registration_id="registration_id",
        )
        assert totp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_disable_with_all_params(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.disable(
            path_registration_id="registration_id",
            code="code",
            body_registration_id="registration_id",
        )
        assert totp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_disable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.totp.with_raw_response.disable(
            path_registration_id="registration_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = response.parse()
        assert totp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_disable(self, client: ScalekitDemo) -> None:
        with client.api.v1.totp.with_streaming_response.disable(
            path_registration_id="registration_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = response.parse()
            assert totp is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_disable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_registration_id` but received ''"):
            client.api.v1.totp.with_raw_response.disable(
                path_registration_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_enable(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.enable(
            path_registration_id="registration_id",
        )
        assert_matches_type(TotpEnableResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_enable_with_all_params(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.enable(
            path_registration_id="registration_id",
            code="code",
            body_registration_id="registration_id",
        )
        assert_matches_type(TotpEnableResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_enable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.totp.with_raw_response.enable(
            path_registration_id="registration_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = response.parse()
        assert_matches_type(TotpEnableResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_enable(self, client: ScalekitDemo) -> None:
        with client.api.v1.totp.with_streaming_response.enable(
            path_registration_id="registration_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = response.parse()
            assert_matches_type(TotpEnableResponse, totp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_enable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_registration_id` but received ''"):
            client.api.v1.totp.with_raw_response.enable(
                path_registration_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_registration(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_registration_with_all_params(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            id="id",
            account_name="account_name",
            update_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="user_id",
        )
        assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_registration(self, client: ScalekitDemo) -> None:
        response = client.api.v1.totp.with_raw_response.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = response.parse()
        assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_registration(self, client: ScalekitDemo) -> None:
        with client.api.v1.totp.with_streaming_response.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = response.parse()
            assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_verify(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.verify(
            path_registration_id="registration_id",
        )
        assert_matches_type(VerifyCodeResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_verify_with_all_params(self, client: ScalekitDemo) -> None:
        totp = client.api.v1.totp.verify(
            path_registration_id="registration_id",
            code="code",
            body_registration_id="registration_id",
        )
        assert_matches_type(VerifyCodeResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_verify(self, client: ScalekitDemo) -> None:
        response = client.api.v1.totp.with_raw_response.verify(
            path_registration_id="registration_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = response.parse()
        assert_matches_type(VerifyCodeResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_verify(self, client: ScalekitDemo) -> None:
        with client.api.v1.totp.with_streaming_response.verify(
            path_registration_id="registration_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = response.parse()
            assert_matches_type(VerifyCodeResponse, totp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_verify(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_registration_id` but received ''"):
            client.api.v1.totp.with_raw_response.verify(
                path_registration_id="",
            )


class TestAsyncTotp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_disable(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.disable(
            path_registration_id="registration_id",
        )
        assert totp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_disable_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.disable(
            path_registration_id="registration_id",
            code="code",
            body_registration_id="registration_id",
        )
        assert totp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_disable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.totp.with_raw_response.disable(
            path_registration_id="registration_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = await response.parse()
        assert totp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_disable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.totp.with_streaming_response.disable(
            path_registration_id="registration_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = await response.parse()
            assert totp is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_disable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_registration_id` but received ''"):
            await async_client.api.v1.totp.with_raw_response.disable(
                path_registration_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_enable(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.enable(
            path_registration_id="registration_id",
        )
        assert_matches_type(TotpEnableResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_enable_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.enable(
            path_registration_id="registration_id",
            code="code",
            body_registration_id="registration_id",
        )
        assert_matches_type(TotpEnableResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_enable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.totp.with_raw_response.enable(
            path_registration_id="registration_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = await response.parse()
        assert_matches_type(TotpEnableResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_enable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.totp.with_streaming_response.enable(
            path_registration_id="registration_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = await response.parse()
            assert_matches_type(TotpEnableResponse, totp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_enable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_registration_id` but received ''"):
            await async_client.api.v1.totp.with_raw_response.enable(
                path_registration_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_registration(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_registration_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            id="id",
            account_name="account_name",
            update_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="user_id",
        )
        assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_registration(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.totp.with_raw_response.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = await response.parse()
        assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_registration(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.totp.with_streaming_response.registration(
            create_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = await response.parse()
            assert_matches_type(TotpRegistrationResponse, totp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_verify(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.verify(
            path_registration_id="registration_id",
        )
        assert_matches_type(VerifyCodeResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_verify_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        totp = await async_client.api.v1.totp.verify(
            path_registration_id="registration_id",
            code="code",
            body_registration_id="registration_id",
        )
        assert_matches_type(VerifyCodeResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_verify(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.totp.with_raw_response.verify(
            path_registration_id="registration_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        totp = await response.parse()
        assert_matches_type(VerifyCodeResponse, totp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_verify(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.totp.with_streaming_response.verify(
            path_registration_id="registration_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            totp = await response.parse()
            assert_matches_type(VerifyCodeResponse, totp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_verify(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_registration_id` but received ''"):
            await async_client.api.v1.totp.with_raw_response.verify(
                path_registration_id="",
            )
