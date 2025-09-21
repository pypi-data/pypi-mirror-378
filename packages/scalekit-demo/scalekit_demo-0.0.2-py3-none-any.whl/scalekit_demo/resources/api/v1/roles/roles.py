# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .permissions import (
    PermissionsResource,
    AsyncPermissionsResource,
    PermissionsResourceWithRawResponse,
    AsyncPermissionsResourceWithRawResponse,
    PermissionsResourceWithStreamingResponse,
    AsyncPermissionsResourceWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1 import (
    role_list_params,
    role_create_params,
    role_delete_params,
    role_update_params,
    role_retrieve_params,
    role_update_default_params,
)
from .....types.api.v1.role_list_response import RoleListResponse
from .....types.api.v1.role_create_response import RoleCreateResponse
from .....types.api.v1.role_update_response import RoleUpdateResponse
from .....types.api.v1.role_retrieve_response import RoleRetrieveResponse
from .....types.api.v1.update_default_role_param import UpdateDefaultRoleParam
from .....types.api.v1.update_default_roles_response import UpdateDefaultRolesResponse
from .....types.api.v1.role_retrieve_dependents_response import RoleRetrieveDependentsResponse
from .....types.api.v1.role_retrieve_users_count_response import RoleRetrieveUsersCountResponse
from .....types.api.v1.role_retrieve_permissions_all_response import RoleRetrievePermissionsAllResponse

__all__ = ["RolesResource", "AsyncRolesResource"]


class RolesResource(SyncAPIResource):
    @cached_property
    def permissions(self) -> PermissionsResource:
        return PermissionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> RolesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return RolesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RolesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return RolesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        extends: str | Omit = omit,
        name: str | Omit = omit,
        permissions: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/roles",
            body=maybe_transform(
                {
                    "description": description,
                    "display_name": display_name,
                    "extends": extends,
                    "name": name,
                    "permissions": permissions,
                },
                role_create_params.RoleCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleCreateResponse,
        )

    def retrieve(
        self,
        role_name: str,
        *,
        include: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return self._get(
            f"/api/v1/roles/{role_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, role_retrieve_params.RoleRetrieveParams),
            ),
            cast_to=RoleRetrieveResponse,
        )

    def update(
        self,
        role_name: str,
        *,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        extends: str | Omit = omit,
        permissions: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleUpdateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return self._put(
            f"/api/v1/roles/{role_name}",
            body=maybe_transform(
                {
                    "description": description,
                    "display_name": display_name,
                    "extends": extends,
                    "permissions": permissions,
                },
                role_update_params.RoleUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleUpdateResponse,
        )

    def list(
        self,
        *,
        include: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/roles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, role_list_params.RoleListParams),
            ),
            cast_to=RoleListResponse,
        )

    def delete(
        self,
        role_name: str,
        *,
        reassign_role_id: str | Omit = omit,
        reassign_role_name: str | Omit = omit,
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
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/roles/{role_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "reassign_role_id": reassign_role_id,
                        "reassign_role_name": reassign_role_name,
                    },
                    role_delete_params.RoleDeleteParams,
                ),
            ),
            cast_to=NoneType,
        )

    def delete_base(
        self,
        role_name: str,
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
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/roles/{role_name}/base",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_dependents(
        self,
        role_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrieveDependentsResponse:
        """
        Role Hierarchy Management RPCs

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return self._get(
            f"/api/v1/roles/{role_name}/dependents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleRetrieveDependentsResponse,
        )

    def retrieve_permissions_all(
        self,
        role_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrievePermissionsAllResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return self._get(
            f"/api/v1/roles/{role_name}/permissions:all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleRetrievePermissionsAllResponse,
        )

    def retrieve_users_count(
        self,
        role_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrieveUsersCountResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return self._get(
            f"/api/v1/roles/{role_name}/users:count",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleRetrieveUsersCountResponse,
        )

    def update_default(
        self,
        *,
        default_creator: UpdateDefaultRoleParam | Omit = omit,
        default_creator_role: str | Omit = omit,
        default_member: UpdateDefaultRoleParam | Omit = omit,
        default_member_role: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateDefaultRolesResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            "/api/v1/roles/default",
            body=maybe_transform(
                {
                    "default_creator": default_creator,
                    "default_creator_role": default_creator_role,
                    "default_member": default_member,
                    "default_member_role": default_member_role,
                },
                role_update_default_params.RoleUpdateDefaultParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDefaultRolesResponse,
        )


class AsyncRolesResource(AsyncAPIResource):
    @cached_property
    def permissions(self) -> AsyncPermissionsResource:
        return AsyncPermissionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRolesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRolesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRolesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncRolesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        extends: str | Omit = omit,
        name: str | Omit = omit,
        permissions: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/roles",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "display_name": display_name,
                    "extends": extends,
                    "name": name,
                    "permissions": permissions,
                },
                role_create_params.RoleCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleCreateResponse,
        )

    async def retrieve(
        self,
        role_name: str,
        *,
        include: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return await self._get(
            f"/api/v1/roles/{role_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"include": include}, role_retrieve_params.RoleRetrieveParams),
            ),
            cast_to=RoleRetrieveResponse,
        )

    async def update(
        self,
        role_name: str,
        *,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        extends: str | Omit = omit,
        permissions: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleUpdateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return await self._put(
            f"/api/v1/roles/{role_name}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "display_name": display_name,
                    "extends": extends,
                    "permissions": permissions,
                },
                role_update_params.RoleUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleUpdateResponse,
        )

    async def list(
        self,
        *,
        include: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/roles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"include": include}, role_list_params.RoleListParams),
            ),
            cast_to=RoleListResponse,
        )

    async def delete(
        self,
        role_name: str,
        *,
        reassign_role_id: str | Omit = omit,
        reassign_role_name: str | Omit = omit,
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
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/roles/{role_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "reassign_role_id": reassign_role_id,
                        "reassign_role_name": reassign_role_name,
                    },
                    role_delete_params.RoleDeleteParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def delete_base(
        self,
        role_name: str,
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
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/roles/{role_name}/base",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_dependents(
        self,
        role_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrieveDependentsResponse:
        """
        Role Hierarchy Management RPCs

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return await self._get(
            f"/api/v1/roles/{role_name}/dependents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleRetrieveDependentsResponse,
        )

    async def retrieve_permissions_all(
        self,
        role_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrievePermissionsAllResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return await self._get(
            f"/api/v1/roles/{role_name}/permissions:all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleRetrievePermissionsAllResponse,
        )

    async def retrieve_users_count(
        self,
        role_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleRetrieveUsersCountResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not role_name:
            raise ValueError(f"Expected a non-empty value for `role_name` but received {role_name!r}")
        return await self._get(
            f"/api/v1/roles/{role_name}/users:count",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleRetrieveUsersCountResponse,
        )

    async def update_default(
        self,
        *,
        default_creator: UpdateDefaultRoleParam | Omit = omit,
        default_creator_role: str | Omit = omit,
        default_member: UpdateDefaultRoleParam | Omit = omit,
        default_member_role: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateDefaultRolesResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            "/api/v1/roles/default",
            body=await async_maybe_transform(
                {
                    "default_creator": default_creator,
                    "default_creator_role": default_creator_role,
                    "default_member": default_member,
                    "default_member_role": default_member_role,
                },
                role_update_default_params.RoleUpdateDefaultParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDefaultRolesResponse,
        )


class RolesResourceWithRawResponse:
    def __init__(self, roles: RolesResource) -> None:
        self._roles = roles

        self.create = to_raw_response_wrapper(
            roles.create,
        )
        self.retrieve = to_raw_response_wrapper(
            roles.retrieve,
        )
        self.update = to_raw_response_wrapper(
            roles.update,
        )
        self.list = to_raw_response_wrapper(
            roles.list,
        )
        self.delete = to_raw_response_wrapper(
            roles.delete,
        )
        self.delete_base = to_raw_response_wrapper(
            roles.delete_base,
        )
        self.retrieve_dependents = to_raw_response_wrapper(
            roles.retrieve_dependents,
        )
        self.retrieve_permissions_all = to_raw_response_wrapper(
            roles.retrieve_permissions_all,
        )
        self.retrieve_users_count = to_raw_response_wrapper(
            roles.retrieve_users_count,
        )
        self.update_default = to_raw_response_wrapper(
            roles.update_default,
        )

    @cached_property
    def permissions(self) -> PermissionsResourceWithRawResponse:
        return PermissionsResourceWithRawResponse(self._roles.permissions)


class AsyncRolesResourceWithRawResponse:
    def __init__(self, roles: AsyncRolesResource) -> None:
        self._roles = roles

        self.create = async_to_raw_response_wrapper(
            roles.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            roles.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            roles.update,
        )
        self.list = async_to_raw_response_wrapper(
            roles.list,
        )
        self.delete = async_to_raw_response_wrapper(
            roles.delete,
        )
        self.delete_base = async_to_raw_response_wrapper(
            roles.delete_base,
        )
        self.retrieve_dependents = async_to_raw_response_wrapper(
            roles.retrieve_dependents,
        )
        self.retrieve_permissions_all = async_to_raw_response_wrapper(
            roles.retrieve_permissions_all,
        )
        self.retrieve_users_count = async_to_raw_response_wrapper(
            roles.retrieve_users_count,
        )
        self.update_default = async_to_raw_response_wrapper(
            roles.update_default,
        )

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithRawResponse:
        return AsyncPermissionsResourceWithRawResponse(self._roles.permissions)


class RolesResourceWithStreamingResponse:
    def __init__(self, roles: RolesResource) -> None:
        self._roles = roles

        self.create = to_streamed_response_wrapper(
            roles.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            roles.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            roles.update,
        )
        self.list = to_streamed_response_wrapper(
            roles.list,
        )
        self.delete = to_streamed_response_wrapper(
            roles.delete,
        )
        self.delete_base = to_streamed_response_wrapper(
            roles.delete_base,
        )
        self.retrieve_dependents = to_streamed_response_wrapper(
            roles.retrieve_dependents,
        )
        self.retrieve_permissions_all = to_streamed_response_wrapper(
            roles.retrieve_permissions_all,
        )
        self.retrieve_users_count = to_streamed_response_wrapper(
            roles.retrieve_users_count,
        )
        self.update_default = to_streamed_response_wrapper(
            roles.update_default,
        )

    @cached_property
    def permissions(self) -> PermissionsResourceWithStreamingResponse:
        return PermissionsResourceWithStreamingResponse(self._roles.permissions)


class AsyncRolesResourceWithStreamingResponse:
    def __init__(self, roles: AsyncRolesResource) -> None:
        self._roles = roles

        self.create = async_to_streamed_response_wrapper(
            roles.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            roles.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            roles.update,
        )
        self.list = async_to_streamed_response_wrapper(
            roles.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            roles.delete,
        )
        self.delete_base = async_to_streamed_response_wrapper(
            roles.delete_base,
        )
        self.retrieve_dependents = async_to_streamed_response_wrapper(
            roles.retrieve_dependents,
        )
        self.retrieve_permissions_all = async_to_streamed_response_wrapper(
            roles.retrieve_permissions_all,
        )
        self.retrieve_users_count = async_to_streamed_response_wrapper(
            roles.retrieve_users_count,
        )
        self.update_default = async_to_streamed_response_wrapper(
            roles.update_default,
        )

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithStreamingResponse:
        return AsyncPermissionsResourceWithStreamingResponse(self._roles.permissions)
