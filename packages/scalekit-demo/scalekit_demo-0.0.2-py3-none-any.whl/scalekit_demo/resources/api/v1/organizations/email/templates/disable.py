# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ......._types import Body, Query, Headers, NoneType, NotGiven, not_given
from ......._compat import cached_property
from ......._resource import SyncAPIResource, AsyncAPIResource
from ......._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......._base_client import make_request_options

__all__ = ["DisableResource", "AsyncDisableResource"]


class DisableResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DisableResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return DisableResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DisableResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return DisableResourceWithStreamingResponse(self)

    def update_template_id_disable(
        self,
        template_id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not template_id:
            raise ValueError(f"Expected a non-empty value for `template_id` but received {template_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._patch(
            f"/api/v1/organizations/{organization_id}/email/templates/{template_id}:disable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncDisableResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDisableResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDisableResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDisableResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncDisableResourceWithStreamingResponse(self)

    async def update_template_id_disable(
        self,
        template_id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not template_id:
            raise ValueError(f"Expected a non-empty value for `template_id` but received {template_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._patch(
            f"/api/v1/organizations/{organization_id}/email/templates/{template_id}:disable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class DisableResourceWithRawResponse:
    def __init__(self, disable: DisableResource) -> None:
        self._disable = disable

        self.update_template_id_disable = to_raw_response_wrapper(
            disable.update_template_id_disable,
        )


class AsyncDisableResourceWithRawResponse:
    def __init__(self, disable: AsyncDisableResource) -> None:
        self._disable = disable

        self.update_template_id_disable = async_to_raw_response_wrapper(
            disable.update_template_id_disable,
        )


class DisableResourceWithStreamingResponse:
    def __init__(self, disable: DisableResource) -> None:
        self._disable = disable

        self.update_template_id_disable = to_streamed_response_wrapper(
            disable.update_template_id_disable,
        )


class AsyncDisableResourceWithStreamingResponse:
    def __init__(self, disable: AsyncDisableResource) -> None:
        self._disable = disable

        self.update_template_id_disable = async_to_streamed_response_wrapper(
            disable.update_template_id_disable,
        )
