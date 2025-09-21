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
from ......types.api.v1.environments.settings import (
    user_management_user_management_params,
    user_management_update_user_management_params,
)
from ......types.api.v1.environments.settings.user_management_user_management_response import (
    UserManagementUserManagementResponse,
)
from ......types.api.v1.environments.settings.user_management_update_user_management_response import (
    UserManagementUpdateUserManagementResponse,
)
from ......types.api.v1.environments.settings.user_management_retrieve_user_management_response import (
    UserManagementRetrieveUserManagementResponse,
)

__all__ = ["UserManagementResource", "AsyncUserManagementResource"]


class UserManagementResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserManagementResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return UserManagementResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserManagementResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return UserManagementResourceWithStreamingResponse(self)

    def retrieve_user_management(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserManagementRetrieveUserManagementResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/environments/{id}/settings/user-management",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserManagementRetrieveUserManagementResponse,
        )

    def update_user_management(
        self,
        id: str,
        *,
        allow_duplicate_user_identities: bool | Omit = omit,
        allow_multiple_memberships: bool | Omit = omit,
        allow_organization_signup: bool | Omit = omit,
        block_disposable_email_domains: bool | Omit = omit,
        block_public_email_domains: bool | Omit = omit,
        enable_max_users_limit: bool | Omit = omit,
        invitation_expiry: int | Omit = omit,
        max_users_limit: int | Omit = omit,
        org_user_relationship: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserManagementUpdateUserManagementResponse:
        """
        Args:
          block_disposable_email_domains: Indicates whether disposable email domains are blocked for user signup/invite.

          block_public_email_domains: Indicates whether public email domains are blocked for user signup/invite.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/api/v1/environments/{id}/settings/user-management",
            body=maybe_transform(
                {
                    "allow_duplicate_user_identities": allow_duplicate_user_identities,
                    "allow_multiple_memberships": allow_multiple_memberships,
                    "allow_organization_signup": allow_organization_signup,
                    "block_disposable_email_domains": block_disposable_email_domains,
                    "block_public_email_domains": block_public_email_domains,
                    "enable_max_users_limit": enable_max_users_limit,
                    "invitation_expiry": invitation_expiry,
                    "max_users_limit": max_users_limit,
                    "org_user_relationship": org_user_relationship,
                },
                user_management_update_user_management_params.UserManagementUpdateUserManagementParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserManagementUpdateUserManagementResponse,
        )

    def user_management(
        self,
        id: str,
        *,
        allow_duplicate_user_identities: bool | Omit = omit,
        allow_multiple_memberships: bool | Omit = omit,
        allow_organization_signup: bool | Omit = omit,
        block_disposable_email_domains: bool | Omit = omit,
        block_public_email_domains: bool | Omit = omit,
        enable_max_users_limit: bool | Omit = omit,
        invitation_expiry: int | Omit = omit,
        max_users_limit: int | Omit = omit,
        org_user_relationship: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserManagementUserManagementResponse:
        """
        Args:
          block_disposable_email_domains: Indicates whether disposable email domains are blocked for user signup/invite.

          block_public_email_domains: Indicates whether public email domains are blocked for user signup/invite.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v1/environments/{id}/settings/user-management",
            body=maybe_transform(
                {
                    "allow_duplicate_user_identities": allow_duplicate_user_identities,
                    "allow_multiple_memberships": allow_multiple_memberships,
                    "allow_organization_signup": allow_organization_signup,
                    "block_disposable_email_domains": block_disposable_email_domains,
                    "block_public_email_domains": block_public_email_domains,
                    "enable_max_users_limit": enable_max_users_limit,
                    "invitation_expiry": invitation_expiry,
                    "max_users_limit": max_users_limit,
                    "org_user_relationship": org_user_relationship,
                },
                user_management_user_management_params.UserManagementUserManagementParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserManagementUserManagementResponse,
        )


class AsyncUserManagementResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserManagementResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUserManagementResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserManagementResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncUserManagementResourceWithStreamingResponse(self)

    async def retrieve_user_management(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserManagementRetrieveUserManagementResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/environments/{id}/settings/user-management",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserManagementRetrieveUserManagementResponse,
        )

    async def update_user_management(
        self,
        id: str,
        *,
        allow_duplicate_user_identities: bool | Omit = omit,
        allow_multiple_memberships: bool | Omit = omit,
        allow_organization_signup: bool | Omit = omit,
        block_disposable_email_domains: bool | Omit = omit,
        block_public_email_domains: bool | Omit = omit,
        enable_max_users_limit: bool | Omit = omit,
        invitation_expiry: int | Omit = omit,
        max_users_limit: int | Omit = omit,
        org_user_relationship: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserManagementUpdateUserManagementResponse:
        """
        Args:
          block_disposable_email_domains: Indicates whether disposable email domains are blocked for user signup/invite.

          block_public_email_domains: Indicates whether public email domains are blocked for user signup/invite.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/api/v1/environments/{id}/settings/user-management",
            body=await async_maybe_transform(
                {
                    "allow_duplicate_user_identities": allow_duplicate_user_identities,
                    "allow_multiple_memberships": allow_multiple_memberships,
                    "allow_organization_signup": allow_organization_signup,
                    "block_disposable_email_domains": block_disposable_email_domains,
                    "block_public_email_domains": block_public_email_domains,
                    "enable_max_users_limit": enable_max_users_limit,
                    "invitation_expiry": invitation_expiry,
                    "max_users_limit": max_users_limit,
                    "org_user_relationship": org_user_relationship,
                },
                user_management_update_user_management_params.UserManagementUpdateUserManagementParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserManagementUpdateUserManagementResponse,
        )

    async def user_management(
        self,
        id: str,
        *,
        allow_duplicate_user_identities: bool | Omit = omit,
        allow_multiple_memberships: bool | Omit = omit,
        allow_organization_signup: bool | Omit = omit,
        block_disposable_email_domains: bool | Omit = omit,
        block_public_email_domains: bool | Omit = omit,
        enable_max_users_limit: bool | Omit = omit,
        invitation_expiry: int | Omit = omit,
        max_users_limit: int | Omit = omit,
        org_user_relationship: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserManagementUserManagementResponse:
        """
        Args:
          block_disposable_email_domains: Indicates whether disposable email domains are blocked for user signup/invite.

          block_public_email_domains: Indicates whether public email domains are blocked for user signup/invite.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v1/environments/{id}/settings/user-management",
            body=await async_maybe_transform(
                {
                    "allow_duplicate_user_identities": allow_duplicate_user_identities,
                    "allow_multiple_memberships": allow_multiple_memberships,
                    "allow_organization_signup": allow_organization_signup,
                    "block_disposable_email_domains": block_disposable_email_domains,
                    "block_public_email_domains": block_public_email_domains,
                    "enable_max_users_limit": enable_max_users_limit,
                    "invitation_expiry": invitation_expiry,
                    "max_users_limit": max_users_limit,
                    "org_user_relationship": org_user_relationship,
                },
                user_management_user_management_params.UserManagementUserManagementParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserManagementUserManagementResponse,
        )


class UserManagementResourceWithRawResponse:
    def __init__(self, user_management: UserManagementResource) -> None:
        self._user_management = user_management

        self.retrieve_user_management = to_raw_response_wrapper(
            user_management.retrieve_user_management,
        )
        self.update_user_management = to_raw_response_wrapper(
            user_management.update_user_management,
        )
        self.user_management = to_raw_response_wrapper(
            user_management.user_management,
        )


class AsyncUserManagementResourceWithRawResponse:
    def __init__(self, user_management: AsyncUserManagementResource) -> None:
        self._user_management = user_management

        self.retrieve_user_management = async_to_raw_response_wrapper(
            user_management.retrieve_user_management,
        )
        self.update_user_management = async_to_raw_response_wrapper(
            user_management.update_user_management,
        )
        self.user_management = async_to_raw_response_wrapper(
            user_management.user_management,
        )


class UserManagementResourceWithStreamingResponse:
    def __init__(self, user_management: UserManagementResource) -> None:
        self._user_management = user_management

        self.retrieve_user_management = to_streamed_response_wrapper(
            user_management.retrieve_user_management,
        )
        self.update_user_management = to_streamed_response_wrapper(
            user_management.update_user_management,
        )
        self.user_management = to_streamed_response_wrapper(
            user_management.user_management,
        )


class AsyncUserManagementResourceWithStreamingResponse:
    def __init__(self, user_management: AsyncUserManagementResource) -> None:
        self._user_management = user_management

        self.retrieve_user_management = async_to_streamed_response_wrapper(
            user_management.retrieve_user_management,
        )
        self.update_user_management = async_to_streamed_response_wrapper(
            user_management.update_user_management,
        )
        self.user_management = async_to_streamed_response_wrapper(
            user_management.user_management,
        )
