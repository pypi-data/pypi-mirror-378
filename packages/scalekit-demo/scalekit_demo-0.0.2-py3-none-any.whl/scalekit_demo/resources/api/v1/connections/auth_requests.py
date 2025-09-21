# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
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
from .....types.api.v1.connections import auth_request_user_params

__all__ = ["AuthRequestsResource", "AsyncAuthRequestsResource"]


class AuthRequestsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AuthRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AuthRequestsResourceWithStreamingResponse(self)

    def user(
        self,
        login_request_id: str,
        *,
        connection_id: str,
        custom_attributes: object | Omit = omit,
        email: str | Omit = omit,
        email_verified: bool | Omit = omit,
        family_name: str | Omit = omit,
        gender: str | Omit = omit,
        given_name: str | Omit = omit,
        groups: SequenceNotStr[str] | Omit = omit,
        locale: str | Omit = omit,
        name: str | Omit = omit,
        phone_number: str | Omit = omit,
        phone_number_verified: bool | Omit = omit,
        picture: str | Omit = omit,
        preferred_username: str | Omit = omit,
        sub: str | Omit = omit,
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
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        if not login_request_id:
            raise ValueError(f"Expected a non-empty value for `login_request_id` but received {login_request_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/connections/{connection_id}/auth-requests/{login_request_id}/user",
            body=maybe_transform(
                {
                    "custom_attributes": custom_attributes,
                    "email": email,
                    "email_verified": email_verified,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "groups": groups,
                    "locale": locale,
                    "name": name,
                    "phone_number": phone_number,
                    "phone_number_verified": phone_number_verified,
                    "picture": picture,
                    "preferred_username": preferred_username,
                    "sub": sub,
                },
                auth_request_user_params.AuthRequestUserParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAuthRequestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncAuthRequestsResourceWithStreamingResponse(self)

    async def user(
        self,
        login_request_id: str,
        *,
        connection_id: str,
        custom_attributes: object | Omit = omit,
        email: str | Omit = omit,
        email_verified: bool | Omit = omit,
        family_name: str | Omit = omit,
        gender: str | Omit = omit,
        given_name: str | Omit = omit,
        groups: SequenceNotStr[str] | Omit = omit,
        locale: str | Omit = omit,
        name: str | Omit = omit,
        phone_number: str | Omit = omit,
        phone_number_verified: bool | Omit = omit,
        picture: str | Omit = omit,
        preferred_username: str | Omit = omit,
        sub: str | Omit = omit,
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
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        if not login_request_id:
            raise ValueError(f"Expected a non-empty value for `login_request_id` but received {login_request_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/connections/{connection_id}/auth-requests/{login_request_id}/user",
            body=await async_maybe_transform(
                {
                    "custom_attributes": custom_attributes,
                    "email": email,
                    "email_verified": email_verified,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "groups": groups,
                    "locale": locale,
                    "name": name,
                    "phone_number": phone_number,
                    "phone_number_verified": phone_number_verified,
                    "picture": picture,
                    "preferred_username": preferred_username,
                    "sub": sub,
                },
                auth_request_user_params.AuthRequestUserParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AuthRequestsResourceWithRawResponse:
    def __init__(self, auth_requests: AuthRequestsResource) -> None:
        self._auth_requests = auth_requests

        self.user = to_raw_response_wrapper(
            auth_requests.user,
        )


class AsyncAuthRequestsResourceWithRawResponse:
    def __init__(self, auth_requests: AsyncAuthRequestsResource) -> None:
        self._auth_requests = auth_requests

        self.user = async_to_raw_response_wrapper(
            auth_requests.user,
        )


class AuthRequestsResourceWithStreamingResponse:
    def __init__(self, auth_requests: AuthRequestsResource) -> None:
        self._auth_requests = auth_requests

        self.user = to_streamed_response_wrapper(
            auth_requests.user,
        )


class AsyncAuthRequestsResourceWithStreamingResponse:
    def __init__(self, auth_requests: AsyncAuthRequestsResource) -> None:
        self._auth_requests = auth_requests

        self.user = async_to_streamed_response_wrapper(
            auth_requests.user,
        )
