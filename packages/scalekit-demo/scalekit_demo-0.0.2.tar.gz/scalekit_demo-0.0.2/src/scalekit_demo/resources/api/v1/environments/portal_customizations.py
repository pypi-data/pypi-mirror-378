# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Query, Headers, NotGiven, not_given
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
from .....types.api.v1.environments import portal_customization_create_params
from .....types.api.v1.update_portal_customization_response import UpdatePortalCustomizationResponse
from .....types.api.v1.environments.get_portal_customization_response import GetPortalCustomizationResponse

__all__ = ["PortalCustomizationsResource", "AsyncPortalCustomizationsResource"]


class PortalCustomizationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PortalCustomizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return PortalCustomizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PortalCustomizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return PortalCustomizationsResourceWithStreamingResponse(self)

    def create(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdatePortalCustomizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/api/v1/environments/{id}/portal_customizations",
            body=maybe_transform(body, portal_customization_create_params.PortalCustomizationCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdatePortalCustomizationResponse,
        )

    def list(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetPortalCustomizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/environments/{id}/portal_customizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetPortalCustomizationResponse,
        )


class AsyncPortalCustomizationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPortalCustomizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPortalCustomizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPortalCustomizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncPortalCustomizationsResourceWithStreamingResponse(self)

    async def create(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdatePortalCustomizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/api/v1/environments/{id}/portal_customizations",
            body=await async_maybe_transform(body, portal_customization_create_params.PortalCustomizationCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdatePortalCustomizationResponse,
        )

    async def list(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetPortalCustomizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/environments/{id}/portal_customizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetPortalCustomizationResponse,
        )


class PortalCustomizationsResourceWithRawResponse:
    def __init__(self, portal_customizations: PortalCustomizationsResource) -> None:
        self._portal_customizations = portal_customizations

        self.create = to_raw_response_wrapper(
            portal_customizations.create,
        )
        self.list = to_raw_response_wrapper(
            portal_customizations.list,
        )


class AsyncPortalCustomizationsResourceWithRawResponse:
    def __init__(self, portal_customizations: AsyncPortalCustomizationsResource) -> None:
        self._portal_customizations = portal_customizations

        self.create = async_to_raw_response_wrapper(
            portal_customizations.create,
        )
        self.list = async_to_raw_response_wrapper(
            portal_customizations.list,
        )


class PortalCustomizationsResourceWithStreamingResponse:
    def __init__(self, portal_customizations: PortalCustomizationsResource) -> None:
        self._portal_customizations = portal_customizations

        self.create = to_streamed_response_wrapper(
            portal_customizations.create,
        )
        self.list = to_streamed_response_wrapper(
            portal_customizations.list,
        )


class AsyncPortalCustomizationsResourceWithStreamingResponse:
    def __init__(self, portal_customizations: AsyncPortalCustomizationsResource) -> None:
        self._portal_customizations = portal_customizations

        self.create = async_to_streamed_response_wrapper(
            portal_customizations.create,
        )
        self.list = async_to_streamed_response_wrapper(
            portal_customizations.list,
        )
