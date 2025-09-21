# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from .roles import (
    RolesResource,
    AsyncRolesResource,
    RolesResourceWithRawResponse,
    AsyncRolesResourceWithRawResponse,
    RolesResourceWithStreamingResponse,
    AsyncRolesResourceWithStreamingResponse,
)
from .domains import (
    DomainsResource,
    AsyncDomainsResource,
    DomainsResourceWithRawResponse,
    AsyncDomainsResourceWithRawResponse,
    DomainsResourceWithStreamingResponse,
    AsyncDomainsResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .connections import (
    ConnectionsResource,
    AsyncConnectionsResource,
    ConnectionsResourceWithRawResponse,
    AsyncConnectionsResourceWithRawResponse,
    ConnectionsResourceWithStreamingResponse,
    AsyncConnectionsResourceWithStreamingResponse,
)
from .email.email import (
    EmailResource,
    AsyncEmailResource,
    EmailResourceWithRawResponse,
    AsyncEmailResourceWithRawResponse,
    EmailResourceWithStreamingResponse,
    AsyncEmailResourceWithStreamingResponse,
)
from .users.users import (
    UsersResource,
    AsyncUsersResource,
    UsersResourceWithRawResponse,
    AsyncUsersResourceWithRawResponse,
    UsersResourceWithStreamingResponse,
    AsyncUsersResourceWithStreamingResponse,
)
from .portal_links import (
    PortalLinksResource,
    AsyncPortalLinksResource,
    PortalLinksResourceWithRawResponse,
    AsyncPortalLinksResourceWithRawResponse,
    PortalLinksResourceWithStreamingResponse,
    AsyncPortalLinksResourceWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .clients.clients import (
    ClientsResource,
    AsyncClientsResource,
    ClientsResourceWithRawResponse,
    AsyncClientsResourceWithRawResponse,
    ClientsResourceWithStreamingResponse,
    AsyncClientsResourceWithStreamingResponse,
)
from ....._base_client import make_request_options
from .....types.api.v1 import (
    organization_list_params,
    organization_create_params,
    organization_delete_params,
    organization_update_params,
    organization_retrieve_params,
    organization_retrieve_users_search_params,
    organization_update_roles_set_defaults_params,
    organization_retrieve_connections_search_params,
)
from .session_settings import (
    SessionSettingsResource,
    AsyncSessionSettingsResource,
    SessionSettingsResourceWithRawResponse,
    AsyncSessionSettingsResourceWithRawResponse,
    SessionSettingsResourceWithStreamingResponse,
    AsyncSessionSettingsResourceWithStreamingResponse,
)
from .settings.settings import (
    SettingsResource,
    AsyncSettingsResource,
    SettingsResourceWithRawResponse,
    AsyncSettingsResourceWithRawResponse,
    SettingsResourceWithStreamingResponse,
    AsyncSettingsResourceWithStreamingResponse,
)
from .directories.directories import (
    DirectoriesResource,
    AsyncDirectoriesResource,
    DirectoriesResourceWithRawResponse,
    AsyncDirectoriesResourceWithRawResponse,
    DirectoriesResourceWithStreamingResponse,
    AsyncDirectoriesResourceWithStreamingResponse,
)
from .....types.api.v1.get_organization_response import GetOrganizationResponse
from .....types.api.v1.organization_list_response import OrganizationListResponse
from .....types.api.v1.organization_create_response import OrganizationCreateResponse
from .....types.api.v1.organization_update_response import OrganizationUpdateResponse
from .....types.api.v1.organization_retrieve_users_search_response import OrganizationRetrieveUsersSearchResponse
from .....types.api.v1.organization_update_roles_set_defaults_response import OrganizationUpdateRolesSetDefaultsResponse
from .....types.api.v1.organization_retrieve_connections_search_response import (
    OrganizationRetrieveConnectionsSearchResponse,
)

__all__ = ["OrganizationsResource", "AsyncOrganizationsResource"]


class OrganizationsResource(SyncAPIResource):
    @cached_property
    def connections(self) -> ConnectionsResource:
        return ConnectionsResource(self._client)

    @cached_property
    def email(self) -> EmailResource:
        return EmailResource(self._client)

    @cached_property
    def portal_links(self) -> PortalLinksResource:
        return PortalLinksResource(self._client)

    @cached_property
    def session_settings(self) -> SessionSettingsResource:
        return SessionSettingsResource(self._client)

    @cached_property
    def settings(self) -> SettingsResource:
        return SettingsResource(self._client)

    @cached_property
    def roles(self) -> RolesResource:
        return RolesResource(self._client)

    @cached_property
    def clients(self) -> ClientsResource:
        return ClientsResource(self._client)

    @cached_property
    def directories(self) -> DirectoriesResource:
        return DirectoriesResource(self._client)

    @cached_property
    def domains(self) -> DomainsResource:
        return DomainsResource(self._client)

    @cached_property
    def users(self) -> UsersResource:
        return UsersResource(self._client)

    @cached_property
    def with_raw_response(self) -> OrganizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return OrganizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrganizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return OrganizationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        display_name: str,
        external_id: str | Omit = omit,
        metadata: Dict[str, str] | Omit = omit,
        region_code: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationCreateResponse:
        """
        Create Organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/organizations",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "external_id": external_id,
                    "metadata": metadata,
                    "region_code": region_code,
                },
                organization_create_params.OrganizationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrganizationCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        external_id: str | Omit = omit,
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
        return self._get(
            f"/api/v1/organizations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"external_id": external_id}, organization_retrieve_params.OrganizationRetrieveParams
                ),
            ),
            cast_to=GetOrganizationResponse,
        )

    def update(
        self,
        id: str,
        *,
        query_external_id: str | Omit = omit,
        update_mask: str | Omit = omit,
        display_name: str | Omit = omit,
        body_external_id: str | Omit = omit,
        metadata: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationUpdateResponse:
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
            f"/api/v1/organizations/{id}",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "body_external_id": body_external_id,
                    "metadata": metadata,
                },
                organization_update_params.OrganizationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "query_external_id": query_external_id,
                        "update_mask": update_mask,
                    },
                    organization_update_params.OrganizationUpdateParams,
                ),
            ),
            cast_to=OrganizationUpdateResponse,
        )

    def list(
        self,
        *,
        external_id: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/organizations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "external_id": external_id,
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    organization_list_params.OrganizationListParams,
                ),
            ),
            cast_to=OrganizationListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        external_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an Organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/organizations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"external_id": external_id}, organization_delete_params.OrganizationDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_connections_search(
        self,
        *,
        connection_type: int | Omit = omit,
        enabled: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        provider: str | Omit = omit,
        query: str | Omit = omit,
        status: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationRetrieveConnectionsSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/organizations/-/connections:search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "connection_type": connection_type,
                        "enabled": enabled,
                        "page_size": page_size,
                        "page_token": page_token,
                        "provider": provider,
                        "query": query,
                        "status": status,
                    },
                    organization_retrieve_connections_search_params.OrganizationRetrieveConnectionsSearchParams,
                ),
            ),
            cast_to=OrganizationRetrieveConnectionsSearchResponse,
        )

    def retrieve_users_search(
        self,
        organization_id: str,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        query: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationRetrieveUsersSearchResponse:
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
            f"/api/v1/organizations/{organization_id}/users:search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                        "query": query,
                    },
                    organization_retrieve_users_search_params.OrganizationRetrieveUsersSearchParams,
                ),
            ),
            cast_to=OrganizationRetrieveUsersSearchResponse,
        )

    def update_roles_set_defaults(
        self,
        path_org_id: str,
        *,
        default_member_role: str | Omit = omit,
        body_org_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationUpdateRolesSetDefaultsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_org_id:
            raise ValueError(f"Expected a non-empty value for `path_org_id` but received {path_org_id!r}")
        return self._patch(
            f"/api/v1/organizations/{path_org_id}/roles:set_defaults",
            body=maybe_transform(
                {
                    "default_member_role": default_member_role,
                    "body_org_id": body_org_id,
                },
                organization_update_roles_set_defaults_params.OrganizationUpdateRolesSetDefaultsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrganizationUpdateRolesSetDefaultsResponse,
        )


class AsyncOrganizationsResource(AsyncAPIResource):
    @cached_property
    def connections(self) -> AsyncConnectionsResource:
        return AsyncConnectionsResource(self._client)

    @cached_property
    def email(self) -> AsyncEmailResource:
        return AsyncEmailResource(self._client)

    @cached_property
    def portal_links(self) -> AsyncPortalLinksResource:
        return AsyncPortalLinksResource(self._client)

    @cached_property
    def session_settings(self) -> AsyncSessionSettingsResource:
        return AsyncSessionSettingsResource(self._client)

    @cached_property
    def settings(self) -> AsyncSettingsResource:
        return AsyncSettingsResource(self._client)

    @cached_property
    def roles(self) -> AsyncRolesResource:
        return AsyncRolesResource(self._client)

    @cached_property
    def clients(self) -> AsyncClientsResource:
        return AsyncClientsResource(self._client)

    @cached_property
    def directories(self) -> AsyncDirectoriesResource:
        return AsyncDirectoriesResource(self._client)

    @cached_property
    def domains(self) -> AsyncDomainsResource:
        return AsyncDomainsResource(self._client)

    @cached_property
    def users(self) -> AsyncUsersResource:
        return AsyncUsersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOrganizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrganizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrganizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncOrganizationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        display_name: str,
        external_id: str | Omit = omit,
        metadata: Dict[str, str] | Omit = omit,
        region_code: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationCreateResponse:
        """
        Create Organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/organizations",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "external_id": external_id,
                    "metadata": metadata,
                    "region_code": region_code,
                },
                organization_create_params.OrganizationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrganizationCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        external_id: str | Omit = omit,
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
        return await self._get(
            f"/api/v1/organizations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"external_id": external_id}, organization_retrieve_params.OrganizationRetrieveParams
                ),
            ),
            cast_to=GetOrganizationResponse,
        )

    async def update(
        self,
        id: str,
        *,
        query_external_id: str | Omit = omit,
        update_mask: str | Omit = omit,
        display_name: str | Omit = omit,
        body_external_id: str | Omit = omit,
        metadata: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationUpdateResponse:
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
            f"/api/v1/organizations/{id}",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "body_external_id": body_external_id,
                    "metadata": metadata,
                },
                organization_update_params.OrganizationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "query_external_id": query_external_id,
                        "update_mask": update_mask,
                    },
                    organization_update_params.OrganizationUpdateParams,
                ),
            ),
            cast_to=OrganizationUpdateResponse,
        )

    async def list(
        self,
        *,
        external_id: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/organizations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "external_id": external_id,
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    organization_list_params.OrganizationListParams,
                ),
            ),
            cast_to=OrganizationListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        external_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an Organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/organizations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"external_id": external_id}, organization_delete_params.OrganizationDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_connections_search(
        self,
        *,
        connection_type: int | Omit = omit,
        enabled: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        provider: str | Omit = omit,
        query: str | Omit = omit,
        status: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationRetrieveConnectionsSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/organizations/-/connections:search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "connection_type": connection_type,
                        "enabled": enabled,
                        "page_size": page_size,
                        "page_token": page_token,
                        "provider": provider,
                        "query": query,
                        "status": status,
                    },
                    organization_retrieve_connections_search_params.OrganizationRetrieveConnectionsSearchParams,
                ),
            ),
            cast_to=OrganizationRetrieveConnectionsSearchResponse,
        )

    async def retrieve_users_search(
        self,
        organization_id: str,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        query: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationRetrieveUsersSearchResponse:
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
            f"/api/v1/organizations/{organization_id}/users:search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                        "query": query,
                    },
                    organization_retrieve_users_search_params.OrganizationRetrieveUsersSearchParams,
                ),
            ),
            cast_to=OrganizationRetrieveUsersSearchResponse,
        )

    async def update_roles_set_defaults(
        self,
        path_org_id: str,
        *,
        default_member_role: str | Omit = omit,
        body_org_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationUpdateRolesSetDefaultsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_org_id:
            raise ValueError(f"Expected a non-empty value for `path_org_id` but received {path_org_id!r}")
        return await self._patch(
            f"/api/v1/organizations/{path_org_id}/roles:set_defaults",
            body=await async_maybe_transform(
                {
                    "default_member_role": default_member_role,
                    "body_org_id": body_org_id,
                },
                organization_update_roles_set_defaults_params.OrganizationUpdateRolesSetDefaultsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrganizationUpdateRolesSetDefaultsResponse,
        )


class OrganizationsResourceWithRawResponse:
    def __init__(self, organizations: OrganizationsResource) -> None:
        self._organizations = organizations

        self.create = to_raw_response_wrapper(
            organizations.create,
        )
        self.retrieve = to_raw_response_wrapper(
            organizations.retrieve,
        )
        self.update = to_raw_response_wrapper(
            organizations.update,
        )
        self.list = to_raw_response_wrapper(
            organizations.list,
        )
        self.delete = to_raw_response_wrapper(
            organizations.delete,
        )
        self.retrieve_connections_search = to_raw_response_wrapper(
            organizations.retrieve_connections_search,
        )
        self.retrieve_users_search = to_raw_response_wrapper(
            organizations.retrieve_users_search,
        )
        self.update_roles_set_defaults = to_raw_response_wrapper(
            organizations.update_roles_set_defaults,
        )

    @cached_property
    def connections(self) -> ConnectionsResourceWithRawResponse:
        return ConnectionsResourceWithRawResponse(self._organizations.connections)

    @cached_property
    def email(self) -> EmailResourceWithRawResponse:
        return EmailResourceWithRawResponse(self._organizations.email)

    @cached_property
    def portal_links(self) -> PortalLinksResourceWithRawResponse:
        return PortalLinksResourceWithRawResponse(self._organizations.portal_links)

    @cached_property
    def session_settings(self) -> SessionSettingsResourceWithRawResponse:
        return SessionSettingsResourceWithRawResponse(self._organizations.session_settings)

    @cached_property
    def settings(self) -> SettingsResourceWithRawResponse:
        return SettingsResourceWithRawResponse(self._organizations.settings)

    @cached_property
    def roles(self) -> RolesResourceWithRawResponse:
        return RolesResourceWithRawResponse(self._organizations.roles)

    @cached_property
    def clients(self) -> ClientsResourceWithRawResponse:
        return ClientsResourceWithRawResponse(self._organizations.clients)

    @cached_property
    def directories(self) -> DirectoriesResourceWithRawResponse:
        return DirectoriesResourceWithRawResponse(self._organizations.directories)

    @cached_property
    def domains(self) -> DomainsResourceWithRawResponse:
        return DomainsResourceWithRawResponse(self._organizations.domains)

    @cached_property
    def users(self) -> UsersResourceWithRawResponse:
        return UsersResourceWithRawResponse(self._organizations.users)


class AsyncOrganizationsResourceWithRawResponse:
    def __init__(self, organizations: AsyncOrganizationsResource) -> None:
        self._organizations = organizations

        self.create = async_to_raw_response_wrapper(
            organizations.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            organizations.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            organizations.update,
        )
        self.list = async_to_raw_response_wrapper(
            organizations.list,
        )
        self.delete = async_to_raw_response_wrapper(
            organizations.delete,
        )
        self.retrieve_connections_search = async_to_raw_response_wrapper(
            organizations.retrieve_connections_search,
        )
        self.retrieve_users_search = async_to_raw_response_wrapper(
            organizations.retrieve_users_search,
        )
        self.update_roles_set_defaults = async_to_raw_response_wrapper(
            organizations.update_roles_set_defaults,
        )

    @cached_property
    def connections(self) -> AsyncConnectionsResourceWithRawResponse:
        return AsyncConnectionsResourceWithRawResponse(self._organizations.connections)

    @cached_property
    def email(self) -> AsyncEmailResourceWithRawResponse:
        return AsyncEmailResourceWithRawResponse(self._organizations.email)

    @cached_property
    def portal_links(self) -> AsyncPortalLinksResourceWithRawResponse:
        return AsyncPortalLinksResourceWithRawResponse(self._organizations.portal_links)

    @cached_property
    def session_settings(self) -> AsyncSessionSettingsResourceWithRawResponse:
        return AsyncSessionSettingsResourceWithRawResponse(self._organizations.session_settings)

    @cached_property
    def settings(self) -> AsyncSettingsResourceWithRawResponse:
        return AsyncSettingsResourceWithRawResponse(self._organizations.settings)

    @cached_property
    def roles(self) -> AsyncRolesResourceWithRawResponse:
        return AsyncRolesResourceWithRawResponse(self._organizations.roles)

    @cached_property
    def clients(self) -> AsyncClientsResourceWithRawResponse:
        return AsyncClientsResourceWithRawResponse(self._organizations.clients)

    @cached_property
    def directories(self) -> AsyncDirectoriesResourceWithRawResponse:
        return AsyncDirectoriesResourceWithRawResponse(self._organizations.directories)

    @cached_property
    def domains(self) -> AsyncDomainsResourceWithRawResponse:
        return AsyncDomainsResourceWithRawResponse(self._organizations.domains)

    @cached_property
    def users(self) -> AsyncUsersResourceWithRawResponse:
        return AsyncUsersResourceWithRawResponse(self._organizations.users)


class OrganizationsResourceWithStreamingResponse:
    def __init__(self, organizations: OrganizationsResource) -> None:
        self._organizations = organizations

        self.create = to_streamed_response_wrapper(
            organizations.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            organizations.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            organizations.update,
        )
        self.list = to_streamed_response_wrapper(
            organizations.list,
        )
        self.delete = to_streamed_response_wrapper(
            organizations.delete,
        )
        self.retrieve_connections_search = to_streamed_response_wrapper(
            organizations.retrieve_connections_search,
        )
        self.retrieve_users_search = to_streamed_response_wrapper(
            organizations.retrieve_users_search,
        )
        self.update_roles_set_defaults = to_streamed_response_wrapper(
            organizations.update_roles_set_defaults,
        )

    @cached_property
    def connections(self) -> ConnectionsResourceWithStreamingResponse:
        return ConnectionsResourceWithStreamingResponse(self._organizations.connections)

    @cached_property
    def email(self) -> EmailResourceWithStreamingResponse:
        return EmailResourceWithStreamingResponse(self._organizations.email)

    @cached_property
    def portal_links(self) -> PortalLinksResourceWithStreamingResponse:
        return PortalLinksResourceWithStreamingResponse(self._organizations.portal_links)

    @cached_property
    def session_settings(self) -> SessionSettingsResourceWithStreamingResponse:
        return SessionSettingsResourceWithStreamingResponse(self._organizations.session_settings)

    @cached_property
    def settings(self) -> SettingsResourceWithStreamingResponse:
        return SettingsResourceWithStreamingResponse(self._organizations.settings)

    @cached_property
    def roles(self) -> RolesResourceWithStreamingResponse:
        return RolesResourceWithStreamingResponse(self._organizations.roles)

    @cached_property
    def clients(self) -> ClientsResourceWithStreamingResponse:
        return ClientsResourceWithStreamingResponse(self._organizations.clients)

    @cached_property
    def directories(self) -> DirectoriesResourceWithStreamingResponse:
        return DirectoriesResourceWithStreamingResponse(self._organizations.directories)

    @cached_property
    def domains(self) -> DomainsResourceWithStreamingResponse:
        return DomainsResourceWithStreamingResponse(self._organizations.domains)

    @cached_property
    def users(self) -> UsersResourceWithStreamingResponse:
        return UsersResourceWithStreamingResponse(self._organizations.users)


class AsyncOrganizationsResourceWithStreamingResponse:
    def __init__(self, organizations: AsyncOrganizationsResource) -> None:
        self._organizations = organizations

        self.create = async_to_streamed_response_wrapper(
            organizations.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            organizations.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            organizations.update,
        )
        self.list = async_to_streamed_response_wrapper(
            organizations.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            organizations.delete,
        )
        self.retrieve_connections_search = async_to_streamed_response_wrapper(
            organizations.retrieve_connections_search,
        )
        self.retrieve_users_search = async_to_streamed_response_wrapper(
            organizations.retrieve_users_search,
        )
        self.update_roles_set_defaults = async_to_streamed_response_wrapper(
            organizations.update_roles_set_defaults,
        )

    @cached_property
    def connections(self) -> AsyncConnectionsResourceWithStreamingResponse:
        return AsyncConnectionsResourceWithStreamingResponse(self._organizations.connections)

    @cached_property
    def email(self) -> AsyncEmailResourceWithStreamingResponse:
        return AsyncEmailResourceWithStreamingResponse(self._organizations.email)

    @cached_property
    def portal_links(self) -> AsyncPortalLinksResourceWithStreamingResponse:
        return AsyncPortalLinksResourceWithStreamingResponse(self._organizations.portal_links)

    @cached_property
    def session_settings(self) -> AsyncSessionSettingsResourceWithStreamingResponse:
        return AsyncSessionSettingsResourceWithStreamingResponse(self._organizations.session_settings)

    @cached_property
    def settings(self) -> AsyncSettingsResourceWithStreamingResponse:
        return AsyncSettingsResourceWithStreamingResponse(self._organizations.settings)

    @cached_property
    def roles(self) -> AsyncRolesResourceWithStreamingResponse:
        return AsyncRolesResourceWithStreamingResponse(self._organizations.roles)

    @cached_property
    def clients(self) -> AsyncClientsResourceWithStreamingResponse:
        return AsyncClientsResourceWithStreamingResponse(self._organizations.clients)

    @cached_property
    def directories(self) -> AsyncDirectoriesResourceWithStreamingResponse:
        return AsyncDirectoriesResourceWithStreamingResponse(self._organizations.directories)

    @cached_property
    def domains(self) -> AsyncDomainsResourceWithStreamingResponse:
        return AsyncDomainsResourceWithStreamingResponse(self._organizations.domains)

    @cached_property
    def users(self) -> AsyncUsersResourceWithStreamingResponse:
        return AsyncUsersResourceWithStreamingResponse(self._organizations.users)
