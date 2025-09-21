# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.email import (
    TemplateRetrieveUsecasesResponse,
    TemplateRetrievePlaceholdersResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTemplates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_placeholders(self, client: ScalekitDemo) -> None:
        template = client.api.v1.email.templates.retrieve_placeholders()
        assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_placeholders_with_all_params(self, client: ScalekitDemo) -> None:
        template = client.api.v1.email.templates.retrieve_placeholders(
            use_case=0,
        )
        assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_placeholders(self, client: ScalekitDemo) -> None:
        response = client.api.v1.email.templates.with_raw_response.retrieve_placeholders()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_placeholders(self, client: ScalekitDemo) -> None:
        with client.api.v1.email.templates.with_streaming_response.retrieve_placeholders() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_usecases(self, client: ScalekitDemo) -> None:
        template = client.api.v1.email.templates.retrieve_usecases()
        assert_matches_type(TemplateRetrieveUsecasesResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_usecases(self, client: ScalekitDemo) -> None:
        response = client.api.v1.email.templates.with_raw_response.retrieve_usecases()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(TemplateRetrieveUsecasesResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_usecases(self, client: ScalekitDemo) -> None:
        with client.api.v1.email.templates.with_streaming_response.retrieve_usecases() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(TemplateRetrieveUsecasesResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTemplates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_placeholders(self, async_client: AsyncScalekitDemo) -> None:
        template = await async_client.api.v1.email.templates.retrieve_placeholders()
        assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_placeholders_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        template = await async_client.api.v1.email.templates.retrieve_placeholders(
            use_case=0,
        )
        assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_placeholders(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.email.templates.with_raw_response.retrieve_placeholders()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = await response.parse()
        assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_placeholders(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.email.templates.with_streaming_response.retrieve_placeholders() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(TemplateRetrievePlaceholdersResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_usecases(self, async_client: AsyncScalekitDemo) -> None:
        template = await async_client.api.v1.email.templates.retrieve_usecases()
        assert_matches_type(TemplateRetrieveUsecasesResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_usecases(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.email.templates.with_raw_response.retrieve_usecases()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = await response.parse()
        assert_matches_type(TemplateRetrieveUsecasesResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_usecases(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.email.templates.with_streaming_response.retrieve_usecases() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(TemplateRetrieveUsecasesResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True
