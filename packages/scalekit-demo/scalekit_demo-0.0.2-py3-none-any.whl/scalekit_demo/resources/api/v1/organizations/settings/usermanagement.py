# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ......_base_client import make_request_options
from ......types.api.v1.organizations.settings import (
    usermanagement_patch_all_params,
)
from ......types.api.v1.organizations.settings.usermanagement_list_response import UsermanagementListResponse
from ......types.api.v1.organizations.settings.usermanagement_patch_all_response import UsermanagementPatchAllResponse
from ......types.api.v1.organizations.settings.organization_user_management_settings_param import (
    OrganizationUserManagementSettingsParam,
)

__all__ = ["UsermanagementResource", "AsyncUsermanagementResource"]


class UsermanagementResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UsermanagementResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return UsermanagementResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsermanagementResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return UsermanagementResourceWithStreamingResponse(self)

    def list(
        self,
        organization_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsermanagementListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get(
            f"/api/v1/organizations/{organization_id}/settings/usermanagement",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UsermanagementListResponse,
        )

    def patch_all(
        self,
        path_organization_id: str,
        *,
        body_organization_id: str | Omit = omit,
        settings: OrganizationUserManagementSettingsParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsermanagementPatchAllResponse:
        """
        Update user management setting for an organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_organization_id:
            raise ValueError(
                f"Expected a non-empty value for `path_organization_id` but received {path_organization_id!r}"
            )
        return self._patch(
            f"/api/v1/organizations/{path_organization_id}/settings/usermanagement",
            body=maybe_transform(
                {
                    "body_organization_id": body_organization_id,
                    "settings": settings,
                },
                usermanagement_patch_all_params.UsermanagementPatchAllParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UsermanagementPatchAllResponse,
        )


class AsyncUsermanagementResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUsermanagementResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUsermanagementResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsermanagementResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncUsermanagementResourceWithStreamingResponse(self)

    async def list(
        self,
        organization_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsermanagementListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return await self._get(
            f"/api/v1/organizations/{organization_id}/settings/usermanagement",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UsermanagementListResponse,
        )

    async def patch_all(
        self,
        path_organization_id: str,
        *,
        body_organization_id: str | Omit = omit,
        settings: OrganizationUserManagementSettingsParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsermanagementPatchAllResponse:
        """
        Update user management setting for an organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_organization_id:
            raise ValueError(
                f"Expected a non-empty value for `path_organization_id` but received {path_organization_id!r}"
            )
        return await self._patch(
            f"/api/v1/organizations/{path_organization_id}/settings/usermanagement",
            body=await async_maybe_transform(
                {
                    "body_organization_id": body_organization_id,
                    "settings": settings,
                },
                usermanagement_patch_all_params.UsermanagementPatchAllParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UsermanagementPatchAllResponse,
        )


class UsermanagementResourceWithRawResponse:
    def __init__(self, usermanagement: UsermanagementResource) -> None:
        self._usermanagement = usermanagement

        self.list = to_raw_response_wrapper(
            usermanagement.list,
        )
        self.patch_all = to_raw_response_wrapper(
            usermanagement.patch_all,
        )


class AsyncUsermanagementResourceWithRawResponse:
    def __init__(self, usermanagement: AsyncUsermanagementResource) -> None:
        self._usermanagement = usermanagement

        self.list = async_to_raw_response_wrapper(
            usermanagement.list,
        )
        self.patch_all = async_to_raw_response_wrapper(
            usermanagement.patch_all,
        )


class UsermanagementResourceWithStreamingResponse:
    def __init__(self, usermanagement: UsermanagementResource) -> None:
        self._usermanagement = usermanagement

        self.list = to_streamed_response_wrapper(
            usermanagement.list,
        )
        self.patch_all = to_streamed_response_wrapper(
            usermanagement.patch_all,
        )


class AsyncUsermanagementResourceWithStreamingResponse:
    def __init__(self, usermanagement: AsyncUsermanagementResource) -> None:
        self._usermanagement = usermanagement

        self.list = async_to_streamed_response_wrapper(
            usermanagement.list,
        )
        self.patch_all = async_to_streamed_response_wrapper(
            usermanagement.patch_all,
        )
