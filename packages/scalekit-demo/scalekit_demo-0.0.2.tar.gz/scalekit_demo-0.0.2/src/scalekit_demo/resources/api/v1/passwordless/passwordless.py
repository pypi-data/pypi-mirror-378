# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .email import (
    EmailResource,
    AsyncEmailResource,
    EmailResourceWithRawResponse,
    AsyncEmailResourceWithRawResponse,
    EmailResourceWithStreamingResponse,
    AsyncEmailResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["PasswordlessResource", "AsyncPasswordlessResource"]


class PasswordlessResource(SyncAPIResource):
    @cached_property
    def email(self) -> EmailResource:
        return EmailResource(self._client)

    @cached_property
    def with_raw_response(self) -> PasswordlessResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return PasswordlessResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PasswordlessResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return PasswordlessResourceWithStreamingResponse(self)


class AsyncPasswordlessResource(AsyncAPIResource):
    @cached_property
    def email(self) -> AsyncEmailResource:
        return AsyncEmailResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPasswordlessResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPasswordlessResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPasswordlessResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncPasswordlessResourceWithStreamingResponse(self)


class PasswordlessResourceWithRawResponse:
    def __init__(self, passwordless: PasswordlessResource) -> None:
        self._passwordless = passwordless

    @cached_property
    def email(self) -> EmailResourceWithRawResponse:
        return EmailResourceWithRawResponse(self._passwordless.email)


class AsyncPasswordlessResourceWithRawResponse:
    def __init__(self, passwordless: AsyncPasswordlessResource) -> None:
        self._passwordless = passwordless

    @cached_property
    def email(self) -> AsyncEmailResourceWithRawResponse:
        return AsyncEmailResourceWithRawResponse(self._passwordless.email)


class PasswordlessResourceWithStreamingResponse:
    def __init__(self, passwordless: PasswordlessResource) -> None:
        self._passwordless = passwordless

    @cached_property
    def email(self) -> EmailResourceWithStreamingResponse:
        return EmailResourceWithStreamingResponse(self._passwordless.email)


class AsyncPasswordlessResourceWithStreamingResponse:
    def __init__(self, passwordless: AsyncPasswordlessResource) -> None:
        self._passwordless = passwordless

    @cached_property
    def email(self) -> AsyncEmailResourceWithStreamingResponse:
        return AsyncEmailResourceWithStreamingResponse(self._passwordless.email)
