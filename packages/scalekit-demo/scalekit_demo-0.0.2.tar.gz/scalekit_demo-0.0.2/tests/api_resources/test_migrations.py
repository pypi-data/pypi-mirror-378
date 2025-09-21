# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types import (
    MigrationCreateFsaDataResponse,
    MigrationCreateStripeCustomersResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMigrations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_fsa_data(self, client: ScalekitDemo) -> None:
        migration = client.migrations.create_fsa_data()
        assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_fsa_data_with_all_params(self, client: ScalekitDemo) -> None:
        migration = client.migrations.create_fsa_data(
            batch_size=0,
            data_type=0,
            environment_ids=["string"],
        )
        assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_fsa_data(self, client: ScalekitDemo) -> None:
        response = client.migrations.with_raw_response.create_fsa_data()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        migration = response.parse()
        assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_fsa_data(self, client: ScalekitDemo) -> None:
        with client.migrations.with_streaming_response.create_fsa_data() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            migration = response.parse()
            assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_stripe_customers(self, client: ScalekitDemo) -> None:
        migration = client.migrations.create_stripe_customers()
        assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_stripe_customers_with_all_params(self, client: ScalekitDemo) -> None:
        migration = client.migrations.create_stripe_customers(
            batch_size=0,
            workspace_ids=["string"],
        )
        assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_stripe_customers(self, client: ScalekitDemo) -> None:
        response = client.migrations.with_raw_response.create_stripe_customers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        migration = response.parse()
        assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_stripe_customers(self, client: ScalekitDemo) -> None:
        with client.migrations.with_streaming_response.create_stripe_customers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            migration = response.parse()
            assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMigrations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_fsa_data(self, async_client: AsyncScalekitDemo) -> None:
        migration = await async_client.migrations.create_fsa_data()
        assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_fsa_data_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        migration = await async_client.migrations.create_fsa_data(
            batch_size=0,
            data_type=0,
            environment_ids=["string"],
        )
        assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_fsa_data(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.migrations.with_raw_response.create_fsa_data()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        migration = await response.parse()
        assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_fsa_data(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.migrations.with_streaming_response.create_fsa_data() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            migration = await response.parse()
            assert_matches_type(MigrationCreateFsaDataResponse, migration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_stripe_customers(self, async_client: AsyncScalekitDemo) -> None:
        migration = await async_client.migrations.create_stripe_customers()
        assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_stripe_customers_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        migration = await async_client.migrations.create_stripe_customers(
            batch_size=0,
            workspace_ids=["string"],
        )
        assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_stripe_customers(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.migrations.with_raw_response.create_stripe_customers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        migration = await response.parse()
        assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_stripe_customers(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.migrations.with_streaming_response.create_stripe_customers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            migration = await response.parse()
            assert_matches_type(MigrationCreateStripeCustomersResponse, migration, path=["response"])

        assert cast(Any, response.is_closed) is True
