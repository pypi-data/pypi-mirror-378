# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import migration_create_fsa_data_params, migration_create_stripe_customers_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.migration_create_fsa_data_response import MigrationCreateFsaDataResponse
from ..types.migration_create_stripe_customers_response import MigrationCreateStripeCustomersResponse

__all__ = ["MigrationsResource", "AsyncMigrationsResource"]


class MigrationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MigrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return MigrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MigrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return MigrationsResourceWithStreamingResponse(self)

    def create_fsa_data(
        self,
        *,
        batch_size: int | Omit = omit,
        data_type: int | Omit = omit,
        environment_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MigrationCreateFsaDataResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/migrations/fsa-data",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "batch_size": batch_size,
                        "data_type": data_type,
                        "environment_ids": environment_ids,
                    },
                    migration_create_fsa_data_params.MigrationCreateFsaDataParams,
                ),
            ),
            cast_to=MigrationCreateFsaDataResponse,
        )

    def create_stripe_customers(
        self,
        *,
        batch_size: int | Omit = omit,
        workspace_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MigrationCreateStripeCustomersResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/migrations/stripe-customers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "batch_size": batch_size,
                        "workspace_ids": workspace_ids,
                    },
                    migration_create_stripe_customers_params.MigrationCreateStripeCustomersParams,
                ),
            ),
            cast_to=MigrationCreateStripeCustomersResponse,
        )


class AsyncMigrationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMigrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMigrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMigrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncMigrationsResourceWithStreamingResponse(self)

    async def create_fsa_data(
        self,
        *,
        batch_size: int | Omit = omit,
        data_type: int | Omit = omit,
        environment_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MigrationCreateFsaDataResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/migrations/fsa-data",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "batch_size": batch_size,
                        "data_type": data_type,
                        "environment_ids": environment_ids,
                    },
                    migration_create_fsa_data_params.MigrationCreateFsaDataParams,
                ),
            ),
            cast_to=MigrationCreateFsaDataResponse,
        )

    async def create_stripe_customers(
        self,
        *,
        batch_size: int | Omit = omit,
        workspace_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MigrationCreateStripeCustomersResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/migrations/stripe-customers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "batch_size": batch_size,
                        "workspace_ids": workspace_ids,
                    },
                    migration_create_stripe_customers_params.MigrationCreateStripeCustomersParams,
                ),
            ),
            cast_to=MigrationCreateStripeCustomersResponse,
        )


class MigrationsResourceWithRawResponse:
    def __init__(self, migrations: MigrationsResource) -> None:
        self._migrations = migrations

        self.create_fsa_data = to_raw_response_wrapper(
            migrations.create_fsa_data,
        )
        self.create_stripe_customers = to_raw_response_wrapper(
            migrations.create_stripe_customers,
        )


class AsyncMigrationsResourceWithRawResponse:
    def __init__(self, migrations: AsyncMigrationsResource) -> None:
        self._migrations = migrations

        self.create_fsa_data = async_to_raw_response_wrapper(
            migrations.create_fsa_data,
        )
        self.create_stripe_customers = async_to_raw_response_wrapper(
            migrations.create_stripe_customers,
        )


class MigrationsResourceWithStreamingResponse:
    def __init__(self, migrations: MigrationsResource) -> None:
        self._migrations = migrations

        self.create_fsa_data = to_streamed_response_wrapper(
            migrations.create_fsa_data,
        )
        self.create_stripe_customers = to_streamed_response_wrapper(
            migrations.create_stripe_customers,
        )


class AsyncMigrationsResourceWithStreamingResponse:
    def __init__(self, migrations: AsyncMigrationsResource) -> None:
        self._migrations = migrations

        self.create_fsa_data = async_to_streamed_response_wrapper(
            migrations.create_fsa_data,
        )
        self.create_stripe_customers = async_to_streamed_response_wrapper(
            migrations.create_stripe_customers,
        )
