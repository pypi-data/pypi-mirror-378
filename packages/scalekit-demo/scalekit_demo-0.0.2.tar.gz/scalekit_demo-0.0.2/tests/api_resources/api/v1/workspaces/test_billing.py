# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.workspaces import (
    BillingRetrievePricingTableResponse,
    BillingRetrieveSubscriptionsResponse,
    BillingRetrieveCustomerPortalResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBilling:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_customer_portal(self, client: ScalekitDemo) -> None:
        billing = client.api.v1.workspaces.billing.retrieve_customer_portal(
            "id",
        )
        assert_matches_type(BillingRetrieveCustomerPortalResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_customer_portal(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces.billing.with_raw_response.retrieve_customer_portal(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = response.parse()
        assert_matches_type(BillingRetrieveCustomerPortalResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_customer_portal(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces.billing.with_streaming_response.retrieve_customer_portal(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = response.parse()
            assert_matches_type(BillingRetrieveCustomerPortalResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_customer_portal(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.workspaces.billing.with_raw_response.retrieve_customer_portal(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_pricing_table(self, client: ScalekitDemo) -> None:
        billing = client.api.v1.workspaces.billing.retrieve_pricing_table(
            "id",
        )
        assert_matches_type(BillingRetrievePricingTableResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_pricing_table(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces.billing.with_raw_response.retrieve_pricing_table(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = response.parse()
        assert_matches_type(BillingRetrievePricingTableResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_pricing_table(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces.billing.with_streaming_response.retrieve_pricing_table(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = response.parse()
            assert_matches_type(BillingRetrievePricingTableResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_pricing_table(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.workspaces.billing.with_raw_response.retrieve_pricing_table(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_subscriptions(self, client: ScalekitDemo) -> None:
        billing = client.api.v1.workspaces.billing.retrieve_subscriptions(
            "id",
        )
        assert_matches_type(BillingRetrieveSubscriptionsResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_subscriptions(self, client: ScalekitDemo) -> None:
        response = client.api.v1.workspaces.billing.with_raw_response.retrieve_subscriptions(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = response.parse()
        assert_matches_type(BillingRetrieveSubscriptionsResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_subscriptions(self, client: ScalekitDemo) -> None:
        with client.api.v1.workspaces.billing.with_streaming_response.retrieve_subscriptions(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = response.parse()
            assert_matches_type(BillingRetrieveSubscriptionsResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_subscriptions(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.workspaces.billing.with_raw_response.retrieve_subscriptions(
                "",
            )


class TestAsyncBilling:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_customer_portal(self, async_client: AsyncScalekitDemo) -> None:
        billing = await async_client.api.v1.workspaces.billing.retrieve_customer_portal(
            "id",
        )
        assert_matches_type(BillingRetrieveCustomerPortalResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_customer_portal(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces.billing.with_raw_response.retrieve_customer_portal(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = await response.parse()
        assert_matches_type(BillingRetrieveCustomerPortalResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_customer_portal(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces.billing.with_streaming_response.retrieve_customer_portal(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = await response.parse()
            assert_matches_type(BillingRetrieveCustomerPortalResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_customer_portal(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.workspaces.billing.with_raw_response.retrieve_customer_portal(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_pricing_table(self, async_client: AsyncScalekitDemo) -> None:
        billing = await async_client.api.v1.workspaces.billing.retrieve_pricing_table(
            "id",
        )
        assert_matches_type(BillingRetrievePricingTableResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_pricing_table(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces.billing.with_raw_response.retrieve_pricing_table(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = await response.parse()
        assert_matches_type(BillingRetrievePricingTableResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_pricing_table(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces.billing.with_streaming_response.retrieve_pricing_table(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = await response.parse()
            assert_matches_type(BillingRetrievePricingTableResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_pricing_table(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.workspaces.billing.with_raw_response.retrieve_pricing_table(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_subscriptions(self, async_client: AsyncScalekitDemo) -> None:
        billing = await async_client.api.v1.workspaces.billing.retrieve_subscriptions(
            "id",
        )
        assert_matches_type(BillingRetrieveSubscriptionsResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_subscriptions(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.workspaces.billing.with_raw_response.retrieve_subscriptions(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = await response.parse()
        assert_matches_type(BillingRetrieveSubscriptionsResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_subscriptions(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.workspaces.billing.with_streaming_response.retrieve_subscriptions(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = await response.parse()
            assert_matches_type(BillingRetrieveSubscriptionsResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_subscriptions(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.workspaces.billing.with_raw_response.retrieve_subscriptions(
                "",
            )
