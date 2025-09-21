# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1.connected_accounts import magic_link_create_params, magic_link_redirect_params
from .....types.api.v1.connected_accounts.magic_link_create_response import MagicLinkCreateResponse
from .....types.api.v1.connected_accounts.magic_link_redirect_response import MagicLinkRedirectResponse

__all__ = ["MagicLinkResource", "AsyncMagicLinkResource"]


class MagicLinkResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MagicLinkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return MagicLinkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MagicLinkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return MagicLinkResourceWithStreamingResponse(self)

    def create(
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
    ) -> MagicLinkCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/connected_accounts/magic_link",
            body=maybe_transform(
                {
                    "id": id,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "user_id": user_id,
                },
                magic_link_create_params.MagicLinkCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MagicLinkCreateResponse,
        )

    def redirect(
        self,
        *,
        redirect_to: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MagicLinkRedirectResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/connected_accounts/magic_link/redirect",
            body=maybe_transform({"redirect_to": redirect_to}, magic_link_redirect_params.MagicLinkRedirectParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MagicLinkRedirectResponse,
        )


class AsyncMagicLinkResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMagicLinkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMagicLinkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMagicLinkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncMagicLinkResourceWithStreamingResponse(self)

    async def create(
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
    ) -> MagicLinkCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/connected_accounts/magic_link",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "user_id": user_id,
                },
                magic_link_create_params.MagicLinkCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MagicLinkCreateResponse,
        )

    async def redirect(
        self,
        *,
        redirect_to: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MagicLinkRedirectResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/connected_accounts/magic_link/redirect",
            body=await async_maybe_transform(
                {"redirect_to": redirect_to}, magic_link_redirect_params.MagicLinkRedirectParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MagicLinkRedirectResponse,
        )


class MagicLinkResourceWithRawResponse:
    def __init__(self, magic_link: MagicLinkResource) -> None:
        self._magic_link = magic_link

        self.create = to_raw_response_wrapper(
            magic_link.create,
        )
        self.redirect = to_raw_response_wrapper(
            magic_link.redirect,
        )


class AsyncMagicLinkResourceWithRawResponse:
    def __init__(self, magic_link: AsyncMagicLinkResource) -> None:
        self._magic_link = magic_link

        self.create = async_to_raw_response_wrapper(
            magic_link.create,
        )
        self.redirect = async_to_raw_response_wrapper(
            magic_link.redirect,
        )


class MagicLinkResourceWithStreamingResponse:
    def __init__(self, magic_link: MagicLinkResource) -> None:
        self._magic_link = magic_link

        self.create = to_streamed_response_wrapper(
            magic_link.create,
        )
        self.redirect = to_streamed_response_wrapper(
            magic_link.redirect,
        )


class AsyncMagicLinkResourceWithStreamingResponse:
    def __init__(self, magic_link: AsyncMagicLinkResource) -> None:
        self._magic_link = magic_link

        self.create = async_to_streamed_response_wrapper(
            magic_link.create,
        )
        self.redirect = async_to_streamed_response_wrapper(
            magic_link.redirect,
        )
