# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ......_types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ......_utils import maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .usermanagement import (
    UsermanagementResource,
    AsyncUsermanagementResource,
    UsermanagementResourceWithRawResponse,
    AsyncUsermanagementResourceWithRawResponse,
    UsermanagementResourceWithStreamingResponse,
    AsyncUsermanagementResourceWithStreamingResponse,
)
from ......_base_client import make_request_options
from ......types.api.v1.organizations import setting_patch_all_params
from ......types.api.v1.get_organization_response import GetOrganizationResponse

__all__ = ["SettingsResource", "AsyncSettingsResource"]


class SettingsResource(SyncAPIResource):
    @cached_property
    def usermanagement(self) -> UsermanagementResource:
        return UsermanagementResource(self._client)

    @cached_property
    def with_raw_response(self) -> SettingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return SettingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SettingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return SettingsResourceWithStreamingResponse(self)

    def patch_all(
        self,
        id: str,
        *,
        features: Iterable[setting_patch_all_params.Feature] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetOrganizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/api/v1/organizations/{id}/settings",
            body=maybe_transform({"features": features}, setting_patch_all_params.SettingPatchAllParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetOrganizationResponse,
        )


class AsyncSettingsResource(AsyncAPIResource):
    @cached_property
    def usermanagement(self) -> AsyncUsermanagementResource:
        return AsyncUsermanagementResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSettingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSettingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSettingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncSettingsResourceWithStreamingResponse(self)

    async def patch_all(
        self,
        id: str,
        *,
        features: Iterable[setting_patch_all_params.Feature] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetOrganizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/api/v1/organizations/{id}/settings",
            body=await async_maybe_transform({"features": features}, setting_patch_all_params.SettingPatchAllParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetOrganizationResponse,
        )


class SettingsResourceWithRawResponse:
    def __init__(self, settings: SettingsResource) -> None:
        self._settings = settings

        self.patch_all = to_raw_response_wrapper(
            settings.patch_all,
        )

    @cached_property
    def usermanagement(self) -> UsermanagementResourceWithRawResponse:
        return UsermanagementResourceWithRawResponse(self._settings.usermanagement)


class AsyncSettingsResourceWithRawResponse:
    def __init__(self, settings: AsyncSettingsResource) -> None:
        self._settings = settings

        self.patch_all = async_to_raw_response_wrapper(
            settings.patch_all,
        )

    @cached_property
    def usermanagement(self) -> AsyncUsermanagementResourceWithRawResponse:
        return AsyncUsermanagementResourceWithRawResponse(self._settings.usermanagement)


class SettingsResourceWithStreamingResponse:
    def __init__(self, settings: SettingsResource) -> None:
        self._settings = settings

        self.patch_all = to_streamed_response_wrapper(
            settings.patch_all,
        )

    @cached_property
    def usermanagement(self) -> UsermanagementResourceWithStreamingResponse:
        return UsermanagementResourceWithStreamingResponse(self._settings.usermanagement)


class AsyncSettingsResourceWithStreamingResponse:
    def __init__(self, settings: AsyncSettingsResource) -> None:
        self._settings = settings

        self.patch_all = async_to_streamed_response_wrapper(
            settings.patch_all,
        )

    @cached_property
    def usermanagement(self) -> AsyncUsermanagementResourceWithStreamingResponse:
        return AsyncUsermanagementResourceWithStreamingResponse(self._settings.usermanagement)
