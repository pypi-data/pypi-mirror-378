# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .consent import (
    ConsentResource,
    AsyncConsentResource,
    ConsentResourceWithRawResponse,
    AsyncConsentResourceWithRawResponse,
    ConsentResourceWithStreamingResponse,
    AsyncConsentResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["OAuthResource", "AsyncOAuthResource"]


class OAuthResource(SyncAPIResource):
    @cached_property
    def consent(self) -> ConsentResource:
        return ConsentResource(self._client)

    @cached_property
    def with_raw_response(self) -> OAuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return OAuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OAuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return OAuthResourceWithStreamingResponse(self)


class AsyncOAuthResource(AsyncAPIResource):
    @cached_property
    def consent(self) -> AsyncConsentResource:
        return AsyncConsentResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOAuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOAuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOAuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncOAuthResourceWithStreamingResponse(self)


class OAuthResourceWithRawResponse:
    def __init__(self, oauth: OAuthResource) -> None:
        self._oauth = oauth

    @cached_property
    def consent(self) -> ConsentResourceWithRawResponse:
        return ConsentResourceWithRawResponse(self._oauth.consent)


class AsyncOAuthResourceWithRawResponse:
    def __init__(self, oauth: AsyncOAuthResource) -> None:
        self._oauth = oauth

    @cached_property
    def consent(self) -> AsyncConsentResourceWithRawResponse:
        return AsyncConsentResourceWithRawResponse(self._oauth.consent)


class OAuthResourceWithStreamingResponse:
    def __init__(self, oauth: OAuthResource) -> None:
        self._oauth = oauth

    @cached_property
    def consent(self) -> ConsentResourceWithStreamingResponse:
        return ConsentResourceWithStreamingResponse(self._oauth.consent)


class AsyncOAuthResourceWithStreamingResponse:
    def __init__(self, oauth: AsyncOAuthResource) -> None:
        self._oauth = oauth

    @cached_property
    def consent(self) -> AsyncConsentResourceWithStreamingResponse:
        return AsyncConsentResourceWithStreamingResponse(self._oauth.consent)
