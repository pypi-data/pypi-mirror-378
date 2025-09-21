# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    GetWorkspaceResponse,
    UpdateWorkspaceResponse,
    WorkspacesThisRetrieveBillingInfoResponse,
    WorkspacesThisRetrieveBillingUsageResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkspacesThis:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_billing_info(self, client: ScalekitDemo) -> None:
        workspaces_this = client.api.v1.workspaces_this.retrieve_billing_info()
        assert_matches_type(WorkspacesThisRetrieveBillingInfoResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_billing_info(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces_this.with_raw_response.retrieve_billing_info()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = response.parse()
        assert_matches_type(WorkspacesThisRetrieveBillingInfoResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_billing_info(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces_this.with_streaming_response.retrieve_billing_info() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = response.parse()
            assert_matches_type(WorkspacesThisRetrieveBillingInfoResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_billing_usage(self, client: ScalekitDemo) -> None:
        workspaces_this = client.api.v1.workspaces_this.retrieve_billing_usage()
        assert_matches_type(WorkspacesThisRetrieveBillingUsageResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_billing_usage(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces_this.with_raw_response.retrieve_billing_usage()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = response.parse()
        assert_matches_type(WorkspacesThisRetrieveBillingUsageResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_billing_usage(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces_this.with_streaming_response.retrieve_billing_usage() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = response.parse()
            assert_matches_type(WorkspacesThisRetrieveBillingUsageResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_workspaces_this(self, client: ScalekitDemo) -> None:
        workspaces_this = client.api.v1.workspaces_this.retrieve_workspaces_this()
        assert_matches_type(GetWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_workspaces_this(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces_this.with_raw_response.retrieve_workspaces_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = response.parse()
        assert_matches_type(GetWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_workspaces_this(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces_this.with_streaming_response.retrieve_workspaces_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = response.parse()
            assert_matches_type(GetWorkspaceResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_workspaces_this(self, client: ScalekitDemo) -> None:
        workspaces_this = client.api.v1.workspaces_this.update_workspaces_this()
        assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_workspaces_this_with_all_params(self, client: ScalekitDemo) -> None:
        workspaces_this = client.api.v1.workspaces_this.update_workspaces_this(
            display_name="display_name",
        )
        assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_workspaces_this(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces_this.with_raw_response.update_workspaces_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = response.parse()
        assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_workspaces_this(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces_this.with_streaming_response.update_workspaces_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = response.parse()
            assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWorkspacesThis:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_billing_info(self, async_client: AsyncScalekitDemo) -> None:
        workspaces_this = await async_client.api.v1.workspaces_this.retrieve_billing_info()
        assert_matches_type(WorkspacesThisRetrieveBillingInfoResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_billing_info(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces_this.with_raw_response.retrieve_billing_info()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = await response.parse()
        assert_matches_type(WorkspacesThisRetrieveBillingInfoResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_billing_info(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces_this.with_streaming_response.retrieve_billing_info() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = await response.parse()
            assert_matches_type(WorkspacesThisRetrieveBillingInfoResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_billing_usage(self, async_client: AsyncScalekitDemo) -> None:
        workspaces_this = await async_client.api.v1.workspaces_this.retrieve_billing_usage()
        assert_matches_type(WorkspacesThisRetrieveBillingUsageResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_billing_usage(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces_this.with_raw_response.retrieve_billing_usage()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = await response.parse()
        assert_matches_type(WorkspacesThisRetrieveBillingUsageResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_billing_usage(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces_this.with_streaming_response.retrieve_billing_usage() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = await response.parse()
            assert_matches_type(WorkspacesThisRetrieveBillingUsageResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_workspaces_this(self, async_client: AsyncScalekitDemo) -> None:
        workspaces_this = await async_client.api.v1.workspaces_this.retrieve_workspaces_this()
        assert_matches_type(GetWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_workspaces_this(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces_this.with_raw_response.retrieve_workspaces_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = await response.parse()
        assert_matches_type(GetWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_workspaces_this(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces_this.with_streaming_response.retrieve_workspaces_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = await response.parse()
            assert_matches_type(GetWorkspaceResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_workspaces_this(self, async_client: AsyncScalekitDemo) -> None:
        workspaces_this = await async_client.api.v1.workspaces_this.update_workspaces_this()
        assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_workspaces_this_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        workspaces_this = await async_client.api.v1.workspaces_this.update_workspaces_this(
            display_name="display_name",
        )
        assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_workspaces_this(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces_this.with_raw_response.update_workspaces_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspaces_this = await response.parse()
        assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_workspaces_this(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces_this.with_streaming_response.update_workspaces_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspaces_this = await response.parse()
            assert_matches_type(UpdateWorkspaceResponse, workspaces_this, path=["response"])

        assert cast(Any, response.is_closed) is True
