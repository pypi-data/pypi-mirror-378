# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime

import httpx

from .groups import (
    GroupsResource,
    AsyncGroupsResource,
    GroupsResourceWithRawResponse,
    AsyncGroupsResourceWithRawResponse,
    GroupsResourceWithStreamingResponse,
    AsyncGroupsResourceWithStreamingResponse,
)
from ......_types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
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
from ......types.api.v1.organizations import (
    directory_create_params,
    directory_update_params,
    directory_retrieve_users_params,
    directory_update_attributes_params,
    directory_update_groups_assign_params,
)
from ......types.api.v1.organizations.directory_list_response import DirectoryListResponse
from ......types.api.v1.organizations.directory_create_response import DirectoryCreateResponse
from ......types.api.v1.organizations.directory_update_response import DirectoryUpdateResponse
from ......types.api.v1.organizations.toggle_directory_response import ToggleDirectoryResponse
from ......types.api.v1.organizations.directory_secrets_response import DirectorySecretsResponse
from ......types.api.v1.organizations.directory_retrieve_response import DirectoryRetrieveResponse
from ......types.api.v1.organizations.directory_retrieve_users_response import DirectoryRetrieveUsersResponse
from ......types.api.v1.organizations.directory_update_attributes_response import DirectoryUpdateAttributesResponse
from ......types.api.v1.organizations.directory_secrets_regenerate_response import DirectorySecretsRegenerateResponse

__all__ = ["DirectoriesResource", "AsyncDirectoriesResource"]


class DirectoriesResource(SyncAPIResource):
    @cached_property
    def groups(self) -> GroupsResource:
        return GroupsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DirectoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return DirectoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DirectoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return DirectoriesResourceWithStreamingResponse(self)

    def create(
        self,
        organization_id: str,
        *,
        directory_provider: int | Omit = omit,
        directory_type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._post(
            f"/api/v1/organizations/{organization_id}/directories",
            body=maybe_transform(
                {
                    "directory_provider": directory_provider,
                    "directory_type": directory_type,
                },
                directory_create_params.DirectoryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryRetrieveResponse:
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
        return self._get(
            f"/api/v1/organizations/{organization_id}/directories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        organization_id: str,
        directory_provider: int | Omit = omit,
        directory_type: int | Omit = omit,
        enabled: bool | Omit = omit,
        groups: Iterable[directory_update_params.Group] | Omit = omit,
        mappings: Iterable[directory_update_params.Mapping] | Omit = omit,
        name: str | Omit = omit,
        status: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryUpdateResponse:
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
        return self._patch(
            f"/api/v1/organizations/{organization_id}/directories/{id}",
            body=maybe_transform(
                {
                    "directory_provider": directory_provider,
                    "directory_type": directory_type,
                    "enabled": enabled,
                    "groups": groups,
                    "mappings": mappings,
                    "name": name,
                    "status": status,
                },
                directory_update_params.DirectoryUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryUpdateResponse,
        )

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
    ) -> DirectoryListResponse:
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
            f"/api/v1/organizations/{organization_id}/directories",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryListResponse,
        )

    def delete(
        self,
        id: str,
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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/organizations/{organization_id}/directories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_directory_id_sync(
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
        if not directory_id:
            raise ValueError(f"Expected a non-empty value for `directory_id` but received {directory_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}:sync",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_users(
        self,
        directory_id: str,
        *,
        organization_id: str,
        directory_group_id: str | Omit = omit,
        include_detail: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        updated_after: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryRetrieveUsersResponse:
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
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/users",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "directory_group_id": directory_group_id,
                        "include_detail": include_detail,
                        "page_size": page_size,
                        "page_token": page_token,
                        "updated_after": updated_after,
                    },
                    directory_retrieve_users_params.DirectoryRetrieveUsersParams,
                ),
            ),
            cast_to=DirectoryRetrieveUsersResponse,
        )

    def secrets(
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
    ) -> DirectorySecretsResponse:
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
        return self._post(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/secrets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectorySecretsResponse,
        )

    def secrets_regenerate(
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
    ) -> DirectorySecretsRegenerateResponse:
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
        return self._post(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/secrets:regenerate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectorySecretsRegenerateResponse,
        )

    def update_attributes(
        self,
        id: str,
        *,
        organization_id: str,
        attributes: Iterable[directory_update_attributes_params.Attribute] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryUpdateAttributesResponse:
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
            f"/api/v1/organizations/{organization_id}/directories/{id}/attributes",
            body=maybe_transform(
                {"attributes": attributes}, directory_update_attributes_params.DirectoryUpdateAttributesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryUpdateAttributesResponse,
        )

    def update_groups_assign(
        self,
        path_id: str,
        *,
        path_organization_id: str,
        body_id: str | Omit = omit,
        external_ids: SequenceNotStr[str] | Omit = omit,
        body_organization_id: str | Omit = omit,
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
        if not path_organization_id:
            raise ValueError(
                f"Expected a non-empty value for `path_organization_id` but received {path_organization_id!r}"
            )
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/api/v1/organizations/{path_organization_id}/directories/{path_id}/groups:assign",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "external_ids": external_ids,
                    "body_organization_id": body_organization_id,
                },
                directory_update_groups_assign_params.DirectoryUpdateGroupsAssignParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update_id_disable(
        self,
        id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleDirectoryResponse:
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
        return self._patch(
            f"/api/v1/organizations/{organization_id}/directories/{id}:disable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleDirectoryResponse,
        )

    def update_id_enable(
        self,
        id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleDirectoryResponse:
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
        return self._patch(
            f"/api/v1/organizations/{organization_id}/directories/{id}:enable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleDirectoryResponse,
        )


class AsyncDirectoriesResource(AsyncAPIResource):
    @cached_property
    def groups(self) -> AsyncGroupsResource:
        return AsyncGroupsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDirectoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDirectoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDirectoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncDirectoriesResourceWithStreamingResponse(self)

    async def create(
        self,
        organization_id: str,
        *,
        directory_provider: int | Omit = omit,
        directory_type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return await self._post(
            f"/api/v1/organizations/{organization_id}/directories",
            body=await async_maybe_transform(
                {
                    "directory_provider": directory_provider,
                    "directory_type": directory_type,
                },
                directory_create_params.DirectoryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryRetrieveResponse:
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
        return await self._get(
            f"/api/v1/organizations/{organization_id}/directories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        organization_id: str,
        directory_provider: int | Omit = omit,
        directory_type: int | Omit = omit,
        enabled: bool | Omit = omit,
        groups: Iterable[directory_update_params.Group] | Omit = omit,
        mappings: Iterable[directory_update_params.Mapping] | Omit = omit,
        name: str | Omit = omit,
        status: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryUpdateResponse:
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
        return await self._patch(
            f"/api/v1/organizations/{organization_id}/directories/{id}",
            body=await async_maybe_transform(
                {
                    "directory_provider": directory_provider,
                    "directory_type": directory_type,
                    "enabled": enabled,
                    "groups": groups,
                    "mappings": mappings,
                    "name": name,
                    "status": status,
                },
                directory_update_params.DirectoryUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryUpdateResponse,
        )

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
    ) -> DirectoryListResponse:
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
            f"/api/v1/organizations/{organization_id}/directories",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryListResponse,
        )

    async def delete(
        self,
        id: str,
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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/organizations/{organization_id}/directories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_directory_id_sync(
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
        if not directory_id:
            raise ValueError(f"Expected a non-empty value for `directory_id` but received {directory_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}:sync",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_users(
        self,
        directory_id: str,
        *,
        organization_id: str,
        directory_group_id: str | Omit = omit,
        include_detail: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        updated_after: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryRetrieveUsersResponse:
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
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/users",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "directory_group_id": directory_group_id,
                        "include_detail": include_detail,
                        "page_size": page_size,
                        "page_token": page_token,
                        "updated_after": updated_after,
                    },
                    directory_retrieve_users_params.DirectoryRetrieveUsersParams,
                ),
            ),
            cast_to=DirectoryRetrieveUsersResponse,
        )

    async def secrets(
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
    ) -> DirectorySecretsResponse:
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
        return await self._post(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/secrets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectorySecretsResponse,
        )

    async def secrets_regenerate(
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
    ) -> DirectorySecretsRegenerateResponse:
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
        return await self._post(
            f"/api/v1/organizations/{organization_id}/directories/{directory_id}/secrets:regenerate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectorySecretsRegenerateResponse,
        )

    async def update_attributes(
        self,
        id: str,
        *,
        organization_id: str,
        attributes: Iterable[directory_update_attributes_params.Attribute] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DirectoryUpdateAttributesResponse:
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
            f"/api/v1/organizations/{organization_id}/directories/{id}/attributes",
            body=await async_maybe_transform(
                {"attributes": attributes}, directory_update_attributes_params.DirectoryUpdateAttributesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DirectoryUpdateAttributesResponse,
        )

    async def update_groups_assign(
        self,
        path_id: str,
        *,
        path_organization_id: str,
        body_id: str | Omit = omit,
        external_ids: SequenceNotStr[str] | Omit = omit,
        body_organization_id: str | Omit = omit,
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
        if not path_organization_id:
            raise ValueError(
                f"Expected a non-empty value for `path_organization_id` but received {path_organization_id!r}"
            )
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/api/v1/organizations/{path_organization_id}/directories/{path_id}/groups:assign",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "external_ids": external_ids,
                    "body_organization_id": body_organization_id,
                },
                directory_update_groups_assign_params.DirectoryUpdateGroupsAssignParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update_id_disable(
        self,
        id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleDirectoryResponse:
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
        return await self._patch(
            f"/api/v1/organizations/{organization_id}/directories/{id}:disable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleDirectoryResponse,
        )

    async def update_id_enable(
        self,
        id: str,
        *,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleDirectoryResponse:
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
        return await self._patch(
            f"/api/v1/organizations/{organization_id}/directories/{id}:enable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleDirectoryResponse,
        )


class DirectoriesResourceWithRawResponse:
    def __init__(self, directories: DirectoriesResource) -> None:
        self._directories = directories

        self.create = to_raw_response_wrapper(
            directories.create,
        )
        self.retrieve = to_raw_response_wrapper(
            directories.retrieve,
        )
        self.update = to_raw_response_wrapper(
            directories.update,
        )
        self.list = to_raw_response_wrapper(
            directories.list,
        )
        self.delete = to_raw_response_wrapper(
            directories.delete,
        )
        self.retrieve_directory_id_sync = to_raw_response_wrapper(
            directories.retrieve_directory_id_sync,
        )
        self.retrieve_users = to_raw_response_wrapper(
            directories.retrieve_users,
        )
        self.secrets = to_raw_response_wrapper(
            directories.secrets,
        )
        self.secrets_regenerate = to_raw_response_wrapper(
            directories.secrets_regenerate,
        )
        self.update_attributes = to_raw_response_wrapper(
            directories.update_attributes,
        )
        self.update_groups_assign = to_raw_response_wrapper(
            directories.update_groups_assign,
        )
        self.update_id_disable = to_raw_response_wrapper(
            directories.update_id_disable,
        )
        self.update_id_enable = to_raw_response_wrapper(
            directories.update_id_enable,
        )

    @cached_property
    def groups(self) -> GroupsResourceWithRawResponse:
        return GroupsResourceWithRawResponse(self._directories.groups)


class AsyncDirectoriesResourceWithRawResponse:
    def __init__(self, directories: AsyncDirectoriesResource) -> None:
        self._directories = directories

        self.create = async_to_raw_response_wrapper(
            directories.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            directories.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            directories.update,
        )
        self.list = async_to_raw_response_wrapper(
            directories.list,
        )
        self.delete = async_to_raw_response_wrapper(
            directories.delete,
        )
        self.retrieve_directory_id_sync = async_to_raw_response_wrapper(
            directories.retrieve_directory_id_sync,
        )
        self.retrieve_users = async_to_raw_response_wrapper(
            directories.retrieve_users,
        )
        self.secrets = async_to_raw_response_wrapper(
            directories.secrets,
        )
        self.secrets_regenerate = async_to_raw_response_wrapper(
            directories.secrets_regenerate,
        )
        self.update_attributes = async_to_raw_response_wrapper(
            directories.update_attributes,
        )
        self.update_groups_assign = async_to_raw_response_wrapper(
            directories.update_groups_assign,
        )
        self.update_id_disable = async_to_raw_response_wrapper(
            directories.update_id_disable,
        )
        self.update_id_enable = async_to_raw_response_wrapper(
            directories.update_id_enable,
        )

    @cached_property
    def groups(self) -> AsyncGroupsResourceWithRawResponse:
        return AsyncGroupsResourceWithRawResponse(self._directories.groups)


class DirectoriesResourceWithStreamingResponse:
    def __init__(self, directories: DirectoriesResource) -> None:
        self._directories = directories

        self.create = to_streamed_response_wrapper(
            directories.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            directories.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            directories.update,
        )
        self.list = to_streamed_response_wrapper(
            directories.list,
        )
        self.delete = to_streamed_response_wrapper(
            directories.delete,
        )
        self.retrieve_directory_id_sync = to_streamed_response_wrapper(
            directories.retrieve_directory_id_sync,
        )
        self.retrieve_users = to_streamed_response_wrapper(
            directories.retrieve_users,
        )
        self.secrets = to_streamed_response_wrapper(
            directories.secrets,
        )
        self.secrets_regenerate = to_streamed_response_wrapper(
            directories.secrets_regenerate,
        )
        self.update_attributes = to_streamed_response_wrapper(
            directories.update_attributes,
        )
        self.update_groups_assign = to_streamed_response_wrapper(
            directories.update_groups_assign,
        )
        self.update_id_disable = to_streamed_response_wrapper(
            directories.update_id_disable,
        )
        self.update_id_enable = to_streamed_response_wrapper(
            directories.update_id_enable,
        )

    @cached_property
    def groups(self) -> GroupsResourceWithStreamingResponse:
        return GroupsResourceWithStreamingResponse(self._directories.groups)


class AsyncDirectoriesResourceWithStreamingResponse:
    def __init__(self, directories: AsyncDirectoriesResource) -> None:
        self._directories = directories

        self.create = async_to_streamed_response_wrapper(
            directories.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            directories.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            directories.update,
        )
        self.list = async_to_streamed_response_wrapper(
            directories.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            directories.delete,
        )
        self.retrieve_directory_id_sync = async_to_streamed_response_wrapper(
            directories.retrieve_directory_id_sync,
        )
        self.retrieve_users = async_to_streamed_response_wrapper(
            directories.retrieve_users,
        )
        self.secrets = async_to_streamed_response_wrapper(
            directories.secrets,
        )
        self.secrets_regenerate = async_to_streamed_response_wrapper(
            directories.secrets_regenerate,
        )
        self.update_attributes = async_to_streamed_response_wrapper(
            directories.update_attributes,
        )
        self.update_groups_assign = async_to_streamed_response_wrapper(
            directories.update_groups_assign,
        )
        self.update_id_disable = async_to_streamed_response_wrapper(
            directories.update_id_disable,
        )
        self.update_id_enable = async_to_streamed_response_wrapper(
            directories.update_id_enable,
        )

    @cached_property
    def groups(self) -> AsyncGroupsResourceWithStreamingResponse:
        return AsyncGroupsResourceWithStreamingResponse(self._directories.groups)
