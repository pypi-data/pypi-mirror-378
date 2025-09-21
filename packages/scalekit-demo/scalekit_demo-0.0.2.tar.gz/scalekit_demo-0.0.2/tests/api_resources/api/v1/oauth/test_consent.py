# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.oauth import ConsentRetrieveDetailsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConsent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_details(self, client: ScalekitDemo) -> None:
        consent = client.api.v1.oauth.consent.retrieve_details()
        assert_matches_type(ConsentRetrieveDetailsResponse, consent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_details(self, client: ScalekitDemo) -> None:
        response = client.api.v1.oauth.consent.with_raw_response.retrieve_details()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        consent = response.parse()
        assert_matches_type(ConsentRetrieveDetailsResponse, consent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_details(self, client: ScalekitDemo) -> None:
        with client.api.v1.oauth.consent.with_streaming_response.retrieve_details() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            consent = response.parse()
            assert_matches_type(ConsentRetrieveDetailsResponse, consent, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConsent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_details(self, async_client: AsyncScalekitDemo) -> None:
        consent = await async_client.api.v1.oauth.consent.retrieve_details()
        assert_matches_type(ConsentRetrieveDetailsResponse, consent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_details(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.oauth.consent.with_raw_response.retrieve_details()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        consent = await response.parse()
        assert_matches_type(ConsentRetrieveDetailsResponse, consent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_details(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.oauth.consent.with_streaming_response.retrieve_details() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            consent = await response.parse()
            assert_matches_type(ConsentRetrieveDetailsResponse, consent, path=["response"])

        assert cast(Any, response.is_closed) is True
