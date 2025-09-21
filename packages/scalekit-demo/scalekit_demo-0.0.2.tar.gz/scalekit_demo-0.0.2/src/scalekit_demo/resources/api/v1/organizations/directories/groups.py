# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime

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
from ......types.api.v1.organizations.directories import group_list_params, group_update_roles_assign_params
from ......types.api.v1.organizations.directories.list_directory_groups_response import ListDirectoryGroupsResponse
from ......types.api.v1.organizations.directories.group_update_roles_assign_response import (
    GroupUpdateRolesAssignResponse,
)

__all__ = ["GroupsResource", "AsyncGroupsResource"]


class GroupsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GroupsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return GroupsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GroupsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return GroupsResourceWithStreamingResponse(self)

    def list(
        self,
        directory_id: str,
        *,
        organization_id: str,
        include_detail: bool | Omit = omit,
        include_external_groups: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        updated_after: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListDirectoryGroupsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not directory_id:
            raise ValueError(f"Expected a non-empty value for `directory_id` but received {directory_id!r}")
        return self._get(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/groups",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_detail": include_detail,
                        "include_external_groups": include_external_groups,
                        "page_size": page_size,
                        "page_token": page_token,
                        "updated_after": updated_after,
                    },
                    group_list_params.GroupListParams,
                ),
            ),
            cast_to=ListDirectoryGroupsResponse,
        )

    def retrieve_summary(
        self,
        directory_id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListDirectoryGroupsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not directory_id:
            raise ValueError(f"Expected a non-empty value for `directory_id` but received {directory_id!r}")
        return self._get(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/groups/summary",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListDirectoryGroupsResponse,
        )

    def update_roles_assign(
        self,
        id: str,
        *,
        organization_id: str,
        assignments: Iterable[group_update_roles_assign_params.Assignment] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GroupUpdateRolesAssignResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/api/v1/organizations/{organization_id}/directories/{id}/groups/-/roles:assign",
            body=maybe_transform(
                {"assignments": assignments}, group_update_roles_assign_params.GroupUpdateRolesAssignParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GroupUpdateRolesAssignResponse,
        )


class AsyncGroupsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGroupsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGroupsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGroupsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncGroupsResourceWithStreamingResponse(self)

    async def list(
        self,
        directory_id: str,
        *,
        organization_id: str,
        include_detail: bool | Omit = omit,
        include_external_groups: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        updated_after: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListDirectoryGroupsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not directory_id:
            raise ValueError(f"Expected a non-empty value for `directory_id` but received {directory_id!r}")
        return await self._get(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/groups",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include_detail": include_detail,
                        "include_external_groups": include_external_groups,
                        "page_size": page_size,
                        "page_token": page_token,
                        "updated_after": updated_after,
                    },
                    group_list_params.GroupListParams,
                ),
            ),
            cast_to=ListDirectoryGroupsResponse,
        )

    async def retrieve_summary(
        self,
        directory_id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListDirectoryGroupsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not directory_id:
            raise ValueError(f"Expected a non-empty value for `directory_id` but received {directory_id!r}")
        return await self._get(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/groups/summary",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListDirectoryGroupsResponse,
        )

    async def update_roles_assign(
        self,
        id: str,
        *,
        organization_id: str,
        assignments: Iterable[group_update_roles_assign_params.Assignment] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GroupUpdateRolesAssignResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/api/v1/organizations/{organization_id}/directories/{id}/groups/-/roles:assign",
            body=await async_maybe_transform(
                {"assignments": assignments}, group_update_roles_assign_params.GroupUpdateRolesAssignParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GroupUpdateRolesAssignResponse,
        )


class GroupsResourceWithRawResponse:
    def __init__(self, groups: GroupsResource) -> None:
        self._groups = groups

        self.list = to_raw_response_wrapper(
            groups.list,
        )
        self.retrieve_summary = to_raw_response_wrapper(
            groups.retrieve_summary,
        )
        self.update_roles_assign = to_raw_response_wrapper(
            groups.update_roles_assign,
        )


class AsyncGroupsResourceWithRawResponse:
    def __init__(self, groups: AsyncGroupsResource) -> None:
        self._groups = groups

        self.list = async_to_raw_response_wrapper(
            groups.list,
        )
        self.retrieve_summary = async_to_raw_response_wrapper(
            groups.retrieve_summary,
        )
        self.update_roles_assign = async_to_raw_response_wrapper(
            groups.update_roles_assign,
        )


class GroupsResourceWithStreamingResponse:
    def __init__(self, groups: GroupsResource) -> None:
        self._groups = groups

        self.list = to_streamed_response_wrapper(
            groups.list,
        )
        self.retrieve_summary = to_streamed_response_wrapper(
            groups.retrieve_summary,
        )
        self.update_roles_assign = to_streamed_response_wrapper(
            groups.update_roles_assign,
        )


class AsyncGroupsResourceWithStreamingResponse:
    def __init__(self, groups: AsyncGroupsResource) -> None:
        self._groups = groups

        self.list = async_to_streamed_response_wrapper(
            groups.list,
        )
        self.retrieve_summary = async_to_streamed_response_wrapper(
            groups.retrieve_summary,
        )
        self.update_roles_assign = async_to_streamed_response_wrapper(
            groups.update_roles_assign,
        )
