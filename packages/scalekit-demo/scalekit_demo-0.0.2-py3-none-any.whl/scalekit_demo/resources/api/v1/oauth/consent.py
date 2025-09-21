# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1.oauth.consent_retrieve_details_response import ConsentRetrieveDetailsResponse

__all__ = ["ConsentResource", "AsyncConsentResource"]


class ConsentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConsentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return ConsentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConsentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return ConsentResourceWithStreamingResponse(self)

    def retrieve_details(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConsentRetrieveDetailsResponse:
        return self._get(
            "/api/v1/oauth/consent/details",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConsentRetrieveDetailsResponse,
        )


class AsyncConsentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConsentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConsentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConsentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncConsentResourceWithStreamingResponse(self)

    async def retrieve_details(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConsentRetrieveDetailsResponse:
        return await self._get(
            "/api/v1/oauth/consent/details",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConsentRetrieveDetailsResponse,
        )


class ConsentResourceWithRawResponse:
    def __init__(self, consent: ConsentResource) -> None:
        self._consent = consent

        self.retrieve_details = to_raw_response_wrapper(
            consent.retrieve_details,
        )


class AsyncConsentResourceWithRawResponse:
    def __init__(self, consent: AsyncConsentResource) -> None:
        self._consent = consent

        self.retrieve_details = async_to_raw_response_wrapper(
            consent.retrieve_details,
        )


class ConsentResourceWithStreamingResponse:
    def __init__(self, consent: ConsentResource) -> None:
        self._consent = consent

        self.retrieve_details = to_streamed_response_wrapper(
            consent.retrieve_details,
        )


class AsyncConsentResourceWithStreamingResponse:
    def __init__(self, consent: AsyncConsentResource) -> None:
        self._consent = consent

        self.retrieve_details = async_to_streamed_response_wrapper(
            consent.retrieve_details,
        )
