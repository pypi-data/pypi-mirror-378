# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ....types.api.v1 import sso_user_attribute_update_params, sso_user_attribute_sso_user_attributes_params
from ....types.api.v1.list_user_attributes_response import ListUserAttributesResponse
from ....types.api.v1.create_user_attribute_response import CreateUserAttributeResponse
from ....types.api.v1.update_user_attribute_response import UpdateUserAttributeResponse

__all__ = ["SSOUserAttributesResource", "AsyncSSOUserAttributesResource"]


class SSOUserAttributesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SSOUserAttributesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return SSOUserAttributesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SSOUserAttributesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return SSOUserAttributesResourceWithStreamingResponse(self)

    def update(
        self,
        path_key: str,
        *,
        datatype: int | Omit = omit,
        directory_user_additional_info: object | Omit = omit,
        enabled: bool | Omit = omit,
        body_key: str | Omit = omit,
        label: str | Omit = omit,
        required: bool | Omit = omit,
        sso_addition_info: sso_user_attribute_update_params.SSOAdditionInfo | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateUserAttributeResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_key:
            raise ValueError(f"Expected a non-empty value for `path_key` but received {path_key!r}")
        return self._patch(
            f"/api/v1/sso-user-attributes/{path_key}",
            body=maybe_transform(
                {
                    "datatype": datatype,
                    "directory_user_additional_info": directory_user_additional_info,
                    "enabled": enabled,
                    "body_key": body_key,
                    "label": label,
                    "required": required,
                    "sso_addition_info": sso_addition_info,
                },
                sso_user_attribute_update_params.SSOUserAttributeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateUserAttributeResponse,
        )

    def delete(
        self,
        key: str,
        *,
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
        if not key:
            raise ValueError(f"Expected a non-empty value for `key` but received {key!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/sso-user-attributes/{key}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_sso_user_attributes(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListUserAttributesResponse:
        return self._get(
            "/api/v1/sso-user-attributes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListUserAttributesResponse,
        )

    def sso_user_attributes(
        self,
        *,
        datatype: int | Omit = omit,
        directory_user_additional_info: object | Omit = omit,
        enabled: bool | Omit = omit,
        key: str | Omit = omit,
        label: str | Omit = omit,
        required: bool | Omit = omit,
        sso_addition_info: sso_user_attribute_sso_user_attributes_params.SSOAdditionInfo | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CreateUserAttributeResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/sso-user-attributes",
            body=maybe_transform(
                {
                    "datatype": datatype,
                    "directory_user_additional_info": directory_user_additional_info,
                    "enabled": enabled,
                    "key": key,
                    "label": label,
                    "required": required,
                    "sso_addition_info": sso_addition_info,
                },
                sso_user_attribute_sso_user_attributes_params.SSOUserAttributeSSOUserAttributesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateUserAttributeResponse,
        )


class AsyncSSOUserAttributesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSSOUserAttributesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSSOUserAttributesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSSOUserAttributesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncSSOUserAttributesResourceWithStreamingResponse(self)

    async def update(
        self,
        path_key: str,
        *,
        datatype: int | Omit = omit,
        directory_user_additional_info: object | Omit = omit,
        enabled: bool | Omit = omit,
        body_key: str | Omit = omit,
        label: str | Omit = omit,
        required: bool | Omit = omit,
        sso_addition_info: sso_user_attribute_update_params.SSOAdditionInfo | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateUserAttributeResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_key:
            raise ValueError(f"Expected a non-empty value for `path_key` but received {path_key!r}")
        return await self._patch(
            f"/api/v1/sso-user-attributes/{path_key}",
            body=await async_maybe_transform(
                {
                    "datatype": datatype,
                    "directory_user_additional_info": directory_user_additional_info,
                    "enabled": enabled,
                    "body_key": body_key,
                    "label": label,
                    "required": required,
                    "sso_addition_info": sso_addition_info,
                },
                sso_user_attribute_update_params.SSOUserAttributeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateUserAttributeResponse,
        )

    async def delete(
        self,
        key: str,
        *,
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
        if not key:
            raise ValueError(f"Expected a non-empty value for `key` but received {key!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/sso-user-attributes/{key}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_sso_user_attributes(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListUserAttributesResponse:
        return await self._get(
            "/api/v1/sso-user-attributes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListUserAttributesResponse,
        )

    async def sso_user_attributes(
        self,
        *,
        datatype: int | Omit = omit,
        directory_user_additional_info: object | Omit = omit,
        enabled: bool | Omit = omit,
        key: str | Omit = omit,
        label: str | Omit = omit,
        required: bool | Omit = omit,
        sso_addition_info: sso_user_attribute_sso_user_attributes_params.SSOAdditionInfo | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CreateUserAttributeResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/sso-user-attributes",
            body=await async_maybe_transform(
                {
                    "datatype": datatype,
                    "directory_user_additional_info": directory_user_additional_info,
                    "enabled": enabled,
                    "key": key,
                    "label": label,
                    "required": required,
                    "sso_addition_info": sso_addition_info,
                },
                sso_user_attribute_sso_user_attributes_params.SSOUserAttributeSSOUserAttributesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateUserAttributeResponse,
        )


class SSOUserAttributesResourceWithRawResponse:
    def __init__(self, sso_user_attributes: SSOUserAttributesResource) -> None:
        self._sso_user_attributes = sso_user_attributes

        self.update = to_raw_response_wrapper(
            sso_user_attributes.update,
        )
        self.delete = to_raw_response_wrapper(
            sso_user_attributes.delete,
        )
        self.retrieve_sso_user_attributes = to_raw_response_wrapper(
            sso_user_attributes.retrieve_sso_user_attributes,
        )
        self.sso_user_attributes = to_raw_response_wrapper(
            sso_user_attributes.sso_user_attributes,
        )


class AsyncSSOUserAttributesResourceWithRawResponse:
    def __init__(self, sso_user_attributes: AsyncSSOUserAttributesResource) -> None:
        self._sso_user_attributes = sso_user_attributes

        self.update = async_to_raw_response_wrapper(
            sso_user_attributes.update,
        )
        self.delete = async_to_raw_response_wrapper(
            sso_user_attributes.delete,
        )
        self.retrieve_sso_user_attributes = async_to_raw_response_wrapper(
            sso_user_attributes.retrieve_sso_user_attributes,
        )
        self.sso_user_attributes = async_to_raw_response_wrapper(
            sso_user_attributes.sso_user_attributes,
        )


class SSOUserAttributesResourceWithStreamingResponse:
    def __init__(self, sso_user_attributes: SSOUserAttributesResource) -> None:
        self._sso_user_attributes = sso_user_attributes

        self.update = to_streamed_response_wrapper(
            sso_user_attributes.update,
        )
        self.delete = to_streamed_response_wrapper(
            sso_user_attributes.delete,
        )
        self.retrieve_sso_user_attributes = to_streamed_response_wrapper(
            sso_user_attributes.retrieve_sso_user_attributes,
        )
        self.sso_user_attributes = to_streamed_response_wrapper(
            sso_user_attributes.sso_user_attributes,
        )


class AsyncSSOUserAttributesResourceWithStreamingResponse:
    def __init__(self, sso_user_attributes: AsyncSSOUserAttributesResource) -> None:
        self._sso_user_attributes = sso_user_attributes

        self.update = async_to_streamed_response_wrapper(
            sso_user_attributes.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            sso_user_attributes.delete,
        )
        self.retrieve_sso_user_attributes = async_to_streamed_response_wrapper(
            sso_user_attributes.retrieve_sso_user_attributes,
        )
        self.sso_user_attributes = async_to_streamed_response_wrapper(
            sso_user_attributes.sso_user_attributes,
        )
