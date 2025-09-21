# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from .magic_link import (
    MagicLinkResource,
    AsyncMagicLinkResource,
    MagicLinkResourceWithRawResponse,
    AsyncMagicLinkResourceWithRawResponse,
    MagicLinkResourceWithStreamingResponse,
    AsyncMagicLinkResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1 import (
    connected_account_list_params,
    connected_account_create_params,
    connected_account_retrieve_auth_params,
)
from .....types.api.v1.connected_account_list_response import ConnectedAccountListResponse
from .....types.api.v1.connected_account_create_response import ConnectedAccountCreateResponse
from .....types.api.v1.connected_account_retrieve_auth_response import ConnectedAccountRetrieveAuthResponse

__all__ = ["ConnectedAccountsResource", "AsyncConnectedAccountsResource"]


class ConnectedAccountsResource(SyncAPIResource):
    @cached_property
    def magic_link(self) -> MagicLinkResource:
        return MagicLinkResource(self._client)

    @cached_property
    def with_raw_response(self) -> ConnectedAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return ConnectedAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConnectedAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return ConnectedAccountsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        connected_account: connected_account_create_params.ConnectedAccount | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedAccountCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/connected_accounts",
            body=maybe_transform(
                {
                    "connected_account": connected_account,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "user_id": user_id,
                },
                connected_account_create_params.ConnectedAccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedAccountCreateResponse,
        )

    def list(
        self,
        *,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        provider: str | Omit = omit,
        query: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedAccountListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/connected_accounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "connector": connector,
                        "identifier": identifier,
                        "organization_id": organization_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "provider": provider,
                        "query": query,
                        "user_id": user_id,
                    },
                    connected_account_list_params.ConnectedAccountListParams,
                ),
            ),
            cast_to=ConnectedAccountListResponse,
        )

    def retrieve_auth(
        self,
        *,
        id: str | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedAccountRetrieveAuthResponse:
        """
        this will return the auth details for a connected account by its identifier

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/connected_accounts/auth",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "connector": connector,
                        "identifier": identifier,
                        "organization_id": organization_id,
                        "user_id": user_id,
                    },
                    connected_account_retrieve_auth_params.ConnectedAccountRetrieveAuthParams,
                ),
            ),
            cast_to=ConnectedAccountRetrieveAuthResponse,
        )


class AsyncConnectedAccountsResource(AsyncAPIResource):
    @cached_property
    def magic_link(self) -> AsyncMagicLinkResource:
        return AsyncMagicLinkResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncConnectedAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConnectedAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConnectedAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncConnectedAccountsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        connected_account: connected_account_create_params.ConnectedAccount | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedAccountCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/connected_accounts",
            body=await async_maybe_transform(
                {
                    "connected_account": connected_account,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "user_id": user_id,
                },
                connected_account_create_params.ConnectedAccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedAccountCreateResponse,
        )

    async def list(
        self,
        *,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        provider: str | Omit = omit,
        query: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedAccountListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/connected_accounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "connector": connector,
                        "identifier": identifier,
                        "organization_id": organization_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "provider": provider,
                        "query": query,
                        "user_id": user_id,
                    },
                    connected_account_list_params.ConnectedAccountListParams,
                ),
            ),
            cast_to=ConnectedAccountListResponse,
        )

    async def retrieve_auth(
        self,
        *,
        id: str | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedAccountRetrieveAuthResponse:
        """
        this will return the auth details for a connected account by its identifier

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/connected_accounts/auth",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "connector": connector,
                        "identifier": identifier,
                        "organization_id": organization_id,
                        "user_id": user_id,
                    },
                    connected_account_retrieve_auth_params.ConnectedAccountRetrieveAuthParams,
                ),
            ),
            cast_to=ConnectedAccountRetrieveAuthResponse,
        )


class ConnectedAccountsResourceWithRawResponse:
    def __init__(self, connected_accounts: ConnectedAccountsResource) -> None:
        self._connected_accounts = connected_accounts

        self.create = to_raw_response_wrapper(
            connected_accounts.create,
        )
        self.list = to_raw_response_wrapper(
            connected_accounts.list,
        )
        self.retrieve_auth = to_raw_response_wrapper(
            connected_accounts.retrieve_auth,
        )

    @cached_property
    def magic_link(self) -> MagicLinkResourceWithRawResponse:
        return MagicLinkResourceWithRawResponse(self._connected_accounts.magic_link)


class AsyncConnectedAccountsResourceWithRawResponse:
    def __init__(self, connected_accounts: AsyncConnectedAccountsResource) -> None:
        self._connected_accounts = connected_accounts

        self.create = async_to_raw_response_wrapper(
            connected_accounts.create,
        )
        self.list = async_to_raw_response_wrapper(
            connected_accounts.list,
        )
        self.retrieve_auth = async_to_raw_response_wrapper(
            connected_accounts.retrieve_auth,
        )

    @cached_property
    def magic_link(self) -> AsyncMagicLinkResourceWithRawResponse:
        return AsyncMagicLinkResourceWithRawResponse(self._connected_accounts.magic_link)


class ConnectedAccountsResourceWithStreamingResponse:
    def __init__(self, connected_accounts: ConnectedAccountsResource) -> None:
        self._connected_accounts = connected_accounts

        self.create = to_streamed_response_wrapper(
            connected_accounts.create,
        )
        self.list = to_streamed_response_wrapper(
            connected_accounts.list,
        )
        self.retrieve_auth = to_streamed_response_wrapper(
            connected_accounts.retrieve_auth,
        )

    @cached_property
    def magic_link(self) -> MagicLinkResourceWithStreamingResponse:
        return MagicLinkResourceWithStreamingResponse(self._connected_accounts.magic_link)


class AsyncConnectedAccountsResourceWithStreamingResponse:
    def __init__(self, connected_accounts: AsyncConnectedAccountsResource) -> None:
        self._connected_accounts = connected_accounts

        self.create = async_to_streamed_response_wrapper(
            connected_accounts.create,
        )
        self.list = async_to_streamed_response_wrapper(
            connected_accounts.list,
        )
        self.retrieve_auth = async_to_streamed_response_wrapper(
            connected_accounts.retrieve_auth,
        )

    @cached_property
    def magic_link(self) -> AsyncMagicLinkResourceWithStreamingResponse:
        return AsyncMagicLinkResourceWithStreamingResponse(self._connected_accounts.magic_link)
