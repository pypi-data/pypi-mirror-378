# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.api.v1 import totp_enable_params, totp_verify_params, totp_disable_params, totp_registration_params
from ....types.api.v1.totp_enable_response import TotpEnableResponse
from ....types.api.v1.verify_code_response import VerifyCodeResponse
from ....types.api.v1.totp_registration_response import TotpRegistrationResponse

__all__ = ["TotpResource", "AsyncTotpResource"]


class TotpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TotpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return TotpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TotpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return TotpResourceWithStreamingResponse(self)

    def disable(
        self,
        path_registration_id: str,
        *,
        code: str | Omit = omit,
        body_registration_id: str | Omit = omit,
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
        if not path_registration_id:
            raise ValueError(
                f"Expected a non-empty value for `path_registration_id` but received {path_registration_id!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/totp/{path_registration_id}/disable",
            body=maybe_transform(
                {
                    "code": code,
                    "body_registration_id": body_registration_id,
                },
                totp_disable_params.TotpDisableParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def enable(
        self,
        path_registration_id: str,
        *,
        code: str | Omit = omit,
        body_registration_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TotpEnableResponse:
        """
        Args:
          code: TODO: Add more validations

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_registration_id:
            raise ValueError(
                f"Expected a non-empty value for `path_registration_id` but received {path_registration_id!r}"
            )
        return self._post(
            f"/api/v1/totp/{path_registration_id}/enable",
            body=maybe_transform(
                {
                    "code": code,
                    "body_registration_id": body_registration_id,
                },
                totp_enable_params.TotpEnableParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TotpEnableResponse,
        )

    def registration(
        self,
        *,
        create_time: Union[str, datetime],
        id: str | Omit = omit,
        account_name: str | Omit = omit,
        update_time: Union[str, datetime] | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TotpRegistrationResponse:
        """
        Enable TOTP for a user

        Args:
          create_time: Created Time

          id: Id

          update_time: Updated time

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/totp/registration",
            body=maybe_transform(
                {
                    "create_time": create_time,
                    "id": id,
                    "account_name": account_name,
                    "update_time": update_time,
                    "user_id": user_id,
                },
                totp_registration_params.TotpRegistrationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TotpRegistrationResponse,
        )

    def verify(
        self,
        path_registration_id: str,
        *,
        code: str | Omit = omit,
        body_registration_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VerifyCodeResponse:
        """
        Verify TOTP code for a registration

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_registration_id:
            raise ValueError(
                f"Expected a non-empty value for `path_registration_id` but received {path_registration_id!r}"
            )
        return self._post(
            f"/api/v1/totp/{path_registration_id}/verify",
            body=maybe_transform(
                {
                    "code": code,
                    "body_registration_id": body_registration_id,
                },
                totp_verify_params.TotpVerifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VerifyCodeResponse,
        )


class AsyncTotpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTotpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTotpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTotpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncTotpResourceWithStreamingResponse(self)

    async def disable(
        self,
        path_registration_id: str,
        *,
        code: str | Omit = omit,
        body_registration_id: str | Omit = omit,
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
        if not path_registration_id:
            raise ValueError(
                f"Expected a non-empty value for `path_registration_id` but received {path_registration_id!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/totp/{path_registration_id}/disable",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "body_registration_id": body_registration_id,
                },
                totp_disable_params.TotpDisableParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def enable(
        self,
        path_registration_id: str,
        *,
        code: str | Omit = omit,
        body_registration_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TotpEnableResponse:
        """
        Args:
          code: TODO: Add more validations

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_registration_id:
            raise ValueError(
                f"Expected a non-empty value for `path_registration_id` but received {path_registration_id!r}"
            )
        return await self._post(
            f"/api/v1/totp/{path_registration_id}/enable",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "body_registration_id": body_registration_id,
                },
                totp_enable_params.TotpEnableParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TotpEnableResponse,
        )

    async def registration(
        self,
        *,
        create_time: Union[str, datetime],
        id: str | Omit = omit,
        account_name: str | Omit = omit,
        update_time: Union[str, datetime] | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TotpRegistrationResponse:
        """
        Enable TOTP for a user

        Args:
          create_time: Created Time

          id: Id

          update_time: Updated time

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/totp/registration",
            body=await async_maybe_transform(
                {
                    "create_time": create_time,
                    "id": id,
                    "account_name": account_name,
                    "update_time": update_time,
                    "user_id": user_id,
                },
                totp_registration_params.TotpRegistrationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TotpRegistrationResponse,
        )

    async def verify(
        self,
        path_registration_id: str,
        *,
        code: str | Omit = omit,
        body_registration_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VerifyCodeResponse:
        """
        Verify TOTP code for a registration

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_registration_id:
            raise ValueError(
                f"Expected a non-empty value for `path_registration_id` but received {path_registration_id!r}"
            )
        return await self._post(
            f"/api/v1/totp/{path_registration_id}/verify",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "body_registration_id": body_registration_id,
                },
                totp_verify_params.TotpVerifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VerifyCodeResponse,
        )


class TotpResourceWithRawResponse:
    def __init__(self, totp: TotpResource) -> None:
        self._totp = totp

        self.disable = to_raw_response_wrapper(
            totp.disable,
        )
        self.enable = to_raw_response_wrapper(
            totp.enable,
        )
        self.registration = to_raw_response_wrapper(
            totp.registration,
        )
        self.verify = to_raw_response_wrapper(
            totp.verify,
        )


class AsyncTotpResourceWithRawResponse:
    def __init__(self, totp: AsyncTotpResource) -> None:
        self._totp = totp

        self.disable = async_to_raw_response_wrapper(
            totp.disable,
        )
        self.enable = async_to_raw_response_wrapper(
            totp.enable,
        )
        self.registration = async_to_raw_response_wrapper(
            totp.registration,
        )
        self.verify = async_to_raw_response_wrapper(
            totp.verify,
        )


class TotpResourceWithStreamingResponse:
    def __init__(self, totp: TotpResource) -> None:
        self._totp = totp

        self.disable = to_streamed_response_wrapper(
            totp.disable,
        )
        self.enable = to_streamed_response_wrapper(
            totp.enable,
        )
        self.registration = to_streamed_response_wrapper(
            totp.registration,
        )
        self.verify = to_streamed_response_wrapper(
            totp.verify,
        )


class AsyncTotpResourceWithStreamingResponse:
    def __init__(self, totp: AsyncTotpResource) -> None:
        self._totp = totp

        self.disable = async_to_streamed_response_wrapper(
            totp.disable,
        )
        self.enable = async_to_streamed_response_wrapper(
            totp.enable,
        )
        self.registration = async_to_streamed_response_wrapper(
            totp.registration,
        )
        self.verify = async_to_streamed_response_wrapper(
            totp.verify,
        )
