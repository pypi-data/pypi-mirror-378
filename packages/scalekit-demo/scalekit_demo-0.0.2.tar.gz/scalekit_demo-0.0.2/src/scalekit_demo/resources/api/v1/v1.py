# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from .mcp import (
    McpResource,
    AsyncMcpResource,
    McpResourceWithRawResponse,
    AsyncMcpResourceWithRawResponse,
    McpResourceWithStreamingResponse,
    AsyncMcpResourceWithStreamingResponse,
)
from .auth import (
    AuthResource,
    AsyncAuthResource,
    AuthResourceWithRawResponse,
    AsyncAuthResourceWithRawResponse,
    AuthResourceWithStreamingResponse,
    AsyncAuthResourceWithStreamingResponse,
)
from .totp import (
    TotpResource,
    AsyncTotpResource,
    TotpResourceWithRawResponse,
    AsyncTotpResourceWithRawResponse,
    TotpResourceWithStreamingResponse,
    AsyncTotpResourceWithStreamingResponse,
)
from .user import (
    UserResource,
    AsyncUserResource,
    UserResourceWithRawResponse,
    AsyncUserResourceWithRawResponse,
    UserResourceWithStreamingResponse,
    AsyncUserResourceWithStreamingResponse,
)
from .tools import (
    ToolsResource,
    AsyncToolsResource,
    ToolsResourceWithRawResponse,
    AsyncToolsResourceWithRawResponse,
    ToolsResourceWithStreamingResponse,
    AsyncToolsResourceWithStreamingResponse,
)
from .events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
from .scopes import (
    ScopesResource,
    AsyncScopesResource,
    ScopesResourceWithRawResponse,
    AsyncScopesResourceWithRawResponse,
    ScopesResourceWithStreamingResponse,
    AsyncScopesResourceWithStreamingResponse,
)
from .billing import (
    BillingResource,
    AsyncBillingResource,
    BillingResourceWithRawResponse,
    AsyncBillingResourceWithRawResponse,
    BillingResourceWithStreamingResponse,
    AsyncBillingResourceWithStreamingResponse,
)
from .members import (
    MembersResource,
    AsyncMembersResource,
    MembersResourceWithRawResponse,
    AsyncMembersResourceWithRawResponse,
    MembersResourceWithStreamingResponse,
    AsyncMembersResourceWithStreamingResponse,
)
from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from .logs.logs import (
    LogsResource,
    AsyncLogsResource,
    LogsResourceWithRawResponse,
    AsyncLogsResourceWithRawResponse,
    LogsResourceWithStreamingResponse,
    AsyncLogsResourceWithStreamingResponse,
)
from .providers import (
    ProvidersResource,
    AsyncProvidersResource,
    ProvidersResourceWithRawResponse,
    AsyncProvidersResourceWithRawResponse,
    ProvidersResourceWithStreamingResponse,
    AsyncProvidersResourceWithStreamingResponse,
)
from ...._compat import cached_property
from .email.email import (
    EmailResource,
    AsyncEmailResource,
    EmailResourceWithRawResponse,
    AsyncEmailResourceWithRawResponse,
    EmailResourceWithStreamingResponse,
    AsyncEmailResourceWithStreamingResponse,
)
from .oauth.oauth import (
    OAuthResource,
    AsyncOAuthResource,
    OAuthResourceWithRawResponse,
    AsyncOAuthResourceWithRawResponse,
    OAuthResourceWithStreamingResponse,
    AsyncOAuthResourceWithStreamingResponse,
)
from .permissions import (
    PermissionsResource,
    AsyncPermissionsResource,
    PermissionsResourceWithRawResponse,
    AsyncPermissionsResourceWithRawResponse,
    PermissionsResourceWithStreamingResponse,
    AsyncPermissionsResourceWithStreamingResponse,
)
from .roles.roles import (
    RolesResource,
    AsyncRolesResource,
    RolesResourceWithRawResponse,
    AsyncRolesResourceWithRawResponse,
    RolesResourceWithStreamingResponse,
    AsyncRolesResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.api import (
    v1_signup_params,
    v1_fetch_bulk_params,
    v1_auth_signup_params,
    v1_execute_tool_params,
    v1_auth_discovery_params,
    v1_tools_set_default_params,
    v1_retrieve_authmethods_params,
    v1_retrieve_sessions_me_params,
    v1_retrieve_users_search_params,
    v1_connected_accounts_delete_params,
    v1_update_roles_set_defaults_params,
    v1_update_workspaces_onboard_params,
    v1_retrieve_organizations_search_params,
    v1_retrieve_connected_accounts_search_params,
)
from .members_this import (
    MembersThisResource,
    AsyncMembersThisResource,
    MembersThisResourceWithRawResponse,
    AsyncMembersThisResourceWithRawResponse,
    MembersThisResourceWithStreamingResponse,
    AsyncMembersThisResourceWithStreamingResponse,
)
from ...._base_client import make_request_options
from .clients.clients import (
    ClientsResource,
    AsyncClientsResource,
    ClientsResourceWithRawResponse,
    AsyncClientsResourceWithRawResponse,
    ClientsResourceWithStreamingResponse,
    AsyncClientsResourceWithStreamingResponse,
)
from .invites.invites import (
    InvitesResource,
    AsyncInvitesResource,
    InvitesResourceWithRawResponse,
    AsyncInvitesResourceWithRawResponse,
    InvitesResourceWithStreamingResponse,
    AsyncInvitesResourceWithStreamingResponse,
)
from .workspaces_this import (
    WorkspacesThisResource,
    AsyncWorkspacesThisResource,
    WorkspacesThisResourceWithRawResponse,
    AsyncWorkspacesThisResourceWithRawResponse,
    WorkspacesThisResourceWithStreamingResponse,
    AsyncWorkspacesThisResourceWithStreamingResponse,
)
from .features.features import (
    FeaturesResource,
    AsyncFeaturesResource,
    FeaturesResourceWithRawResponse,
    AsyncFeaturesResourceWithRawResponse,
    FeaturesResourceWithStreamingResponse,
    AsyncFeaturesResourceWithStreamingResponse,
)
from .webhooks.webhooks import (
    WebhooksResource,
    AsyncWebhooksResource,
    WebhooksResourceWithRawResponse,
    AsyncWebhooksResourceWithRawResponse,
    WebhooksResourceWithStreamingResponse,
    AsyncWebhooksResourceWithStreamingResponse,
)
from .resources.resources import (
    ResourcesResource,
    AsyncResourcesResource,
    ResourcesResourceWithRawResponse,
    AsyncResourcesResourceWithRawResponse,
    ResourcesResourceWithStreamingResponse,
    AsyncResourcesResourceWithStreamingResponse,
)
from .sso_user_attributes import (
    SSOUserAttributesResource,
    AsyncSSOUserAttributesResource,
    SSOUserAttributesResourceWithRawResponse,
    AsyncSSOUserAttributesResourceWithRawResponse,
    SSOUserAttributesResourceWithStreamingResponse,
    AsyncSSOUserAttributesResourceWithStreamingResponse,
)
from .workspaces.workspaces import (
    WorkspacesResource,
    AsyncWorkspacesResource,
    WorkspacesResourceWithRawResponse,
    AsyncWorkspacesResourceWithRawResponse,
    WorkspacesResourceWithStreamingResponse,
    AsyncWorkspacesResourceWithStreamingResponse,
)
from .connections.connections import (
    ConnectionsResource,
    AsyncConnectionsResource,
    ConnectionsResourceWithRawResponse,
    AsyncConnectionsResourceWithRawResponse,
    ConnectionsResourceWithStreamingResponse,
    AsyncConnectionsResourceWithStreamingResponse,
)
from .memberships.memberships import (
    MembershipsResource,
    AsyncMembershipsResource,
    MembershipsResourceWithRawResponse,
    AsyncMembershipsResourceWithRawResponse,
    MembershipsResourceWithStreamingResponse,
    AsyncMembershipsResourceWithStreamingResponse,
)
from .user_profile_attributes import (
    UserProfileAttributesResource,
    AsyncUserProfileAttributesResource,
    UserProfileAttributesResourceWithRawResponse,
    AsyncUserProfileAttributesResourceWithRawResponse,
    UserProfileAttributesResourceWithStreamingResponse,
    AsyncUserProfileAttributesResourceWithStreamingResponse,
)
from .directory_user_attributes import (
    DirectoryUserAttributesResource,
    AsyncDirectoryUserAttributesResource,
    DirectoryUserAttributesResourceWithRawResponse,
    AsyncDirectoryUserAttributesResourceWithRawResponse,
    DirectoryUserAttributesResourceWithStreamingResponse,
    AsyncDirectoryUserAttributesResourceWithStreamingResponse,
)
from .environments.environments import (
    EnvironmentsResource,
    AsyncEnvironmentsResource,
    EnvironmentsResourceWithRawResponse,
    AsyncEnvironmentsResourceWithRawResponse,
    EnvironmentsResourceWithStreamingResponse,
    AsyncEnvironmentsResourceWithStreamingResponse,
)
from .passwordless.passwordless import (
    PasswordlessResource,
    AsyncPasswordlessResource,
    PasswordlessResourceWithRawResponse,
    AsyncPasswordlessResourceWithRawResponse,
    PasswordlessResourceWithStreamingResponse,
    AsyncPasswordlessResourceWithStreamingResponse,
)
from .organizations.organizations import (
    OrganizationsResource,
    AsyncOrganizationsResource,
    OrganizationsResourceWithRawResponse,
    AsyncOrganizationsResourceWithRawResponse,
    OrganizationsResourceWithStreamingResponse,
    AsyncOrganizationsResourceWithStreamingResponse,
)
from ....types.api.v1_signup_response import V1SignupResponse
from ....types.api.v1_retrieve_response import V1RetrieveResponse
from ....types.api.v1_fetch_bulk_response import V1FetchBulkResponse
from ....types.api.v1_auth_signup_response import V1AuthSignupResponse
from ....types.api.v1_execute_tool_response import V1ExecuteToolResponse
from .connected_accounts.connected_accounts import (
    ConnectedAccountsResource,
    AsyncConnectedAccountsResource,
    ConnectedAccountsResourceWithRawResponse,
    AsyncConnectedAccountsResourceWithRawResponse,
    ConnectedAccountsResourceWithStreamingResponse,
    AsyncConnectedAccountsResourceWithStreamingResponse,
)
from ....types.api.v1_auth_discovery_response import V1AuthDiscoveryResponse
from ....types.api.v1.update_default_role_param import UpdateDefaultRoleParam
from ....types.api.v1_tools_set_default_response import V1ToolsSetDefaultResponse
from ....types.api.v1.update_default_roles_response import UpdateDefaultRolesResponse
from ....types.api.v1_retrieve_authmethods_response import V1RetrieveAuthmethodsResponse
from ....types.api.v1_retrieve_users_search_response import V1RetrieveUsersSearchResponse
from ....types.api.v1_retrieve_auth_features_response import V1RetrieveAuthFeaturesResponse
from ....types.api.v1_retrieve_auth_organizations_response import V1RetrieveAuthOrganizationsResponse
from ....types.api.v1_retrieve_auth_customizations_response import V1RetrieveAuthCustomizationsResponse
from ....types.api.v1_retrieve_organizations_search_response import V1RetrieveOrganizationsSearchResponse
from ....types.api.v1.environments.get_current_session_response import GetCurrentSessionResponse
from ....types.api.v1_retrieve_connected_accounts_search_response import V1RetrieveConnectedAccountsSearchResponse

__all__ = ["V1Resource", "AsyncV1Resource"]


class V1Resource(SyncAPIResource):
    @cached_property
    def auth(self) -> AuthResource:
        return AuthResource(self._client)

    @cached_property
    def billing(self) -> BillingResource:
        return BillingResource(self._client)

    @cached_property
    def clients(self) -> ClientsResource:
        return ClientsResource(self._client)

    @cached_property
    def connected_accounts(self) -> ConnectedAccountsResource:
        return ConnectedAccountsResource(self._client)

    @cached_property
    def connections(self) -> ConnectionsResource:
        return ConnectionsResource(self._client)

    @cached_property
    def directory_user_attributes(self) -> DirectoryUserAttributesResource:
        return DirectoryUserAttributesResource(self._client)

    @cached_property
    def environments(self) -> EnvironmentsResource:
        return EnvironmentsResource(self._client)

    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def features(self) -> FeaturesResource:
        return FeaturesResource(self._client)

    @cached_property
    def invites(self) -> InvitesResource:
        return InvitesResource(self._client)

    @cached_property
    def logs(self) -> LogsResource:
        return LogsResource(self._client)

    @cached_property
    def mcp(self) -> McpResource:
        return McpResource(self._client)

    @cached_property
    def members(self) -> MembersResource:
        return MembersResource(self._client)

    @cached_property
    def members_this(self) -> MembersThisResource:
        return MembersThisResource(self._client)

    @cached_property
    def memberships(self) -> MembershipsResource:
        return MembershipsResource(self._client)

    @cached_property
    def oauth(self) -> OAuthResource:
        return OAuthResource(self._client)

    @cached_property
    def organizations(self) -> OrganizationsResource:
        return OrganizationsResource(self._client)

    @cached_property
    def passwordless(self) -> PasswordlessResource:
        return PasswordlessResource(self._client)

    @cached_property
    def permissions(self) -> PermissionsResource:
        return PermissionsResource(self._client)

    @cached_property
    def providers(self) -> ProvidersResource:
        return ProvidersResource(self._client)

    @cached_property
    def resources(self) -> ResourcesResource:
        return ResourcesResource(self._client)

    @cached_property
    def roles(self) -> RolesResource:
        return RolesResource(self._client)

    @cached_property
    def scopes(self) -> ScopesResource:
        return ScopesResource(self._client)

    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def sso_user_attributes(self) -> SSOUserAttributesResource:
        return SSOUserAttributesResource(self._client)

    @cached_property
    def tools(self) -> ToolsResource:
        return ToolsResource(self._client)

    @cached_property
    def totp(self) -> TotpResource:
        return TotpResource(self._client)

    @cached_property
    def user_profile_attributes(self) -> UserProfileAttributesResource:
        return UserProfileAttributesResource(self._client)

    @cached_property
    def webhooks(self) -> WebhooksResource:
        return WebhooksResource(self._client)

    @cached_property
    def workspaces(self) -> WorkspacesResource:
        return WorkspacesResource(self._client)

    @cached_property
    def workspaces_this(self) -> WorkspacesThisResource:
        return WorkspacesThisResource(self._client)

    @cached_property
    def email(self) -> EmailResource:
        return EmailResource(self._client)

    @cached_property
    def user(self) -> UserResource:
        return UserResource(self._client)

    @cached_property
    def with_raw_response(self) -> V1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return V1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return V1ResourceWithStreamingResponse(self)

    def retrieve(
        self,
        origin: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not origin:
            raise ValueError(f"Expected a non-empty value for `origin` but received {origin!r}")
        return self._get(
            f"/api/v1/domains/{origin}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveResponse,
        )

    def auth_discovery(
        self,
        *,
        email: str | Omit = omit,
        intent: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1AuthDiscoveryResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/auth:discovery",
            body=maybe_transform(
                {
                    "email": email,
                    "intent": intent,
                },
                v1_auth_discovery_params.V1AuthDiscoveryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1AuthDiscoveryResponse,
        )

    def auth_signup(
        self,
        *,
        first_name: str | Omit = omit,
        full_name: str | Omit = omit,
        last_name: str | Omit = omit,
        organization_name: str | Omit = omit,
        phone_number: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1AuthSignupResponse:
        """
        Args:
          organization_name: making all optional for now

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/auth:signup",
            body=maybe_transform(
                {
                    "first_name": first_name,
                    "full_name": full_name,
                    "last_name": last_name,
                    "organization_name": organization_name,
                    "phone_number": phone_number,
                },
                v1_auth_signup_params.V1AuthSignupParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1AuthSignupResponse,
        )

    def connected_accounts_delete(
        self,
        *,
        id: str | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/connected_accounts:delete",
            body=maybe_transform(
                {
                    "id": id,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "user_id": user_id,
                },
                v1_connected_accounts_delete_params.V1ConnectedAccountsDeleteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def execute_tool(
        self,
        *,
        connected_account_id: str | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        params: object | Omit = omit,
        tool_name: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1ExecuteToolResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/execute_tool",
            body=maybe_transform(
                {
                    "connected_account_id": connected_account_id,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "params": params,
                    "tool_name": tool_name,
                    "user_id": user_id,
                },
                v1_execute_tool_params.V1ExecuteToolParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1ExecuteToolResponse,
        )

    def fetch_bulk(
        self,
        *,
        resources: Iterable[v1_fetch_bulk_params.Resource] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1FetchBulkResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/fetch:bulk",
            body=maybe_transform({"resources": resources}, v1_fetch_bulk_params.V1FetchBulkParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1FetchBulkResponse,
        )

    def retrieve_auth_customizations(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthCustomizationsResponse:
        return self._get(
            "/api/v1/auth:customizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveAuthCustomizationsResponse,
        )

    def retrieve_auth_features(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthFeaturesResponse:
        return self._get(
            "/api/v1/auth:features",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveAuthFeaturesResponse,
        )

    def retrieve_auth_organizations(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthOrganizationsResponse:
        return self._get(
            "/api/v1/auth:organizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveAuthOrganizationsResponse,
        )

    def retrieve_authmethods(
        self,
        *,
        intent: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthmethodsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/authmethods",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"intent": intent}, v1_retrieve_authmethods_params.V1RetrieveAuthmethodsParams),
            ),
            cast_to=V1RetrieveAuthmethodsResponse,
        )

    def retrieve_connected_accounts_search(
        self,
        *,
        connection_id: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        query: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveConnectedAccountsSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/connected_accounts:search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "connection_id": connection_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "query": query,
                    },
                    v1_retrieve_connected_accounts_search_params.V1RetrieveConnectedAccountsSearchParams,
                ),
            ),
            cast_to=V1RetrieveConnectedAccountsSearchResponse,
        )

    def retrieve_organizations_search(
        self,
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
    ) -> V1RetrieveOrganizationsSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/organizations:search",
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
                    v1_retrieve_organizations_search_params.V1RetrieveOrganizationsSearchParams,
                ),
            ),
            cast_to=V1RetrieveOrganizationsSearchResponse,
        )

    def retrieve_session_active(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/session:active",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_sessions_me(
        self,
        *,
        id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetCurrentSessionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/sessions:me",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"id": id}, v1_retrieve_sessions_me_params.V1RetrieveSessionsMeParams),
            ),
            cast_to=GetCurrentSessionResponse,
        )

    def retrieve_users_search(
        self,
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
    ) -> V1RetrieveUsersSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/users:search",
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
                    v1_retrieve_users_search_params.V1RetrieveUsersSearchParams,
                ),
            ),
            cast_to=V1RetrieveUsersSearchResponse,
        )

    def signup(
        self,
        *,
        company: str | Omit = omit,
        email: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1SignupResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/signup",
            body=maybe_transform(
                {
                    "company": company,
                    "email": email,
                },
                v1_signup_params.V1SignupParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1SignupResponse,
        )

    def tools_set_default(
        self,
        *,
        name: str | Omit = omit,
        schema_version: str | Omit = omit,
        tool_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1ToolsSetDefaultResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/tools:set_default",
            body=maybe_transform(
                {
                    "name": name,
                    "schema_version": schema_version,
                    "tool_version": tool_version,
                },
                v1_tools_set_default_params.V1ToolsSetDefaultParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1ToolsSetDefaultResponse,
        )

    def update_roles_set_defaults(
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
            "/api/v1/roles:set_defaults",
            body=maybe_transform(
                {
                    "default_creator": default_creator,
                    "default_creator_role": default_creator_role,
                    "default_member": default_member,
                    "default_member_role": default_member_role,
                },
                v1_update_roles_set_defaults_params.V1UpdateRolesSetDefaultsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDefaultRolesResponse,
        )

    def update_workspaces_onboard(
        self,
        *,
        user_family_name: str | Omit = omit,
        user_given_name: str | Omit = omit,
        workspace_display_name: str | Omit = omit,
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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._patch(
            "/api/v1/workspaces:onboard",
            body=maybe_transform(
                {
                    "user_family_name": user_family_name,
                    "user_given_name": user_given_name,
                    "workspace_display_name": workspace_display_name,
                },
                v1_update_workspaces_onboard_params.V1UpdateWorkspacesOnboardParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncV1Resource(AsyncAPIResource):
    @cached_property
    def auth(self) -> AsyncAuthResource:
        return AsyncAuthResource(self._client)

    @cached_property
    def billing(self) -> AsyncBillingResource:
        return AsyncBillingResource(self._client)

    @cached_property
    def clients(self) -> AsyncClientsResource:
        return AsyncClientsResource(self._client)

    @cached_property
    def connected_accounts(self) -> AsyncConnectedAccountsResource:
        return AsyncConnectedAccountsResource(self._client)

    @cached_property
    def connections(self) -> AsyncConnectionsResource:
        return AsyncConnectionsResource(self._client)

    @cached_property
    def directory_user_attributes(self) -> AsyncDirectoryUserAttributesResource:
        return AsyncDirectoryUserAttributesResource(self._client)

    @cached_property
    def environments(self) -> AsyncEnvironmentsResource:
        return AsyncEnvironmentsResource(self._client)

    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def features(self) -> AsyncFeaturesResource:
        return AsyncFeaturesResource(self._client)

    @cached_property
    def invites(self) -> AsyncInvitesResource:
        return AsyncInvitesResource(self._client)

    @cached_property
    def logs(self) -> AsyncLogsResource:
        return AsyncLogsResource(self._client)

    @cached_property
    def mcp(self) -> AsyncMcpResource:
        return AsyncMcpResource(self._client)

    @cached_property
    def members(self) -> AsyncMembersResource:
        return AsyncMembersResource(self._client)

    @cached_property
    def members_this(self) -> AsyncMembersThisResource:
        return AsyncMembersThisResource(self._client)

    @cached_property
    def memberships(self) -> AsyncMembershipsResource:
        return AsyncMembershipsResource(self._client)

    @cached_property
    def oauth(self) -> AsyncOAuthResource:
        return AsyncOAuthResource(self._client)

    @cached_property
    def organizations(self) -> AsyncOrganizationsResource:
        return AsyncOrganizationsResource(self._client)

    @cached_property
    def passwordless(self) -> AsyncPasswordlessResource:
        return AsyncPasswordlessResource(self._client)

    @cached_property
    def permissions(self) -> AsyncPermissionsResource:
        return AsyncPermissionsResource(self._client)

    @cached_property
    def providers(self) -> AsyncProvidersResource:
        return AsyncProvidersResource(self._client)

    @cached_property
    def resources(self) -> AsyncResourcesResource:
        return AsyncResourcesResource(self._client)

    @cached_property
    def roles(self) -> AsyncRolesResource:
        return AsyncRolesResource(self._client)

    @cached_property
    def scopes(self) -> AsyncScopesResource:
        return AsyncScopesResource(self._client)

    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def sso_user_attributes(self) -> AsyncSSOUserAttributesResource:
        return AsyncSSOUserAttributesResource(self._client)

    @cached_property
    def tools(self) -> AsyncToolsResource:
        return AsyncToolsResource(self._client)

    @cached_property
    def totp(self) -> AsyncTotpResource:
        return AsyncTotpResource(self._client)

    @cached_property
    def user_profile_attributes(self) -> AsyncUserProfileAttributesResource:
        return AsyncUserProfileAttributesResource(self._client)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResource:
        return AsyncWebhooksResource(self._client)

    @cached_property
    def workspaces(self) -> AsyncWorkspacesResource:
        return AsyncWorkspacesResource(self._client)

    @cached_property
    def workspaces_this(self) -> AsyncWorkspacesThisResource:
        return AsyncWorkspacesThisResource(self._client)

    @cached_property
    def email(self) -> AsyncEmailResource:
        return AsyncEmailResource(self._client)

    @cached_property
    def user(self) -> AsyncUserResource:
        return AsyncUserResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncV1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncV1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncV1ResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        origin: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not origin:
            raise ValueError(f"Expected a non-empty value for `origin` but received {origin!r}")
        return await self._get(
            f"/api/v1/domains/{origin}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveResponse,
        )

    async def auth_discovery(
        self,
        *,
        email: str | Omit = omit,
        intent: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1AuthDiscoveryResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/auth:discovery",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "intent": intent,
                },
                v1_auth_discovery_params.V1AuthDiscoveryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1AuthDiscoveryResponse,
        )

    async def auth_signup(
        self,
        *,
        first_name: str | Omit = omit,
        full_name: str | Omit = omit,
        last_name: str | Omit = omit,
        organization_name: str | Omit = omit,
        phone_number: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1AuthSignupResponse:
        """
        Args:
          organization_name: making all optional for now

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/auth:signup",
            body=await async_maybe_transform(
                {
                    "first_name": first_name,
                    "full_name": full_name,
                    "last_name": last_name,
                    "organization_name": organization_name,
                    "phone_number": phone_number,
                },
                v1_auth_signup_params.V1AuthSignupParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1AuthSignupResponse,
        )

    async def connected_accounts_delete(
        self,
        *,
        id: str | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/connected_accounts:delete",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "user_id": user_id,
                },
                v1_connected_accounts_delete_params.V1ConnectedAccountsDeleteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def execute_tool(
        self,
        *,
        connected_account_id: str | Omit = omit,
        connector: str | Omit = omit,
        identifier: str | Omit = omit,
        organization_id: str | Omit = omit,
        params: object | Omit = omit,
        tool_name: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1ExecuteToolResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/execute_tool",
            body=await async_maybe_transform(
                {
                    "connected_account_id": connected_account_id,
                    "connector": connector,
                    "identifier": identifier,
                    "organization_id": organization_id,
                    "params": params,
                    "tool_name": tool_name,
                    "user_id": user_id,
                },
                v1_execute_tool_params.V1ExecuteToolParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1ExecuteToolResponse,
        )

    async def fetch_bulk(
        self,
        *,
        resources: Iterable[v1_fetch_bulk_params.Resource] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1FetchBulkResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/fetch:bulk",
            body=await async_maybe_transform({"resources": resources}, v1_fetch_bulk_params.V1FetchBulkParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1FetchBulkResponse,
        )

    async def retrieve_auth_customizations(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthCustomizationsResponse:
        return await self._get(
            "/api/v1/auth:customizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveAuthCustomizationsResponse,
        )

    async def retrieve_auth_features(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthFeaturesResponse:
        return await self._get(
            "/api/v1/auth:features",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveAuthFeaturesResponse,
        )

    async def retrieve_auth_organizations(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthOrganizationsResponse:
        return await self._get(
            "/api/v1/auth:organizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1RetrieveAuthOrganizationsResponse,
        )

    async def retrieve_authmethods(
        self,
        *,
        intent: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveAuthmethodsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/authmethods",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"intent": intent}, v1_retrieve_authmethods_params.V1RetrieveAuthmethodsParams
                ),
            ),
            cast_to=V1RetrieveAuthmethodsResponse,
        )

    async def retrieve_connected_accounts_search(
        self,
        *,
        connection_id: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        query: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1RetrieveConnectedAccountsSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/connected_accounts:search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "connection_id": connection_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "query": query,
                    },
                    v1_retrieve_connected_accounts_search_params.V1RetrieveConnectedAccountsSearchParams,
                ),
            ),
            cast_to=V1RetrieveConnectedAccountsSearchResponse,
        )

    async def retrieve_organizations_search(
        self,
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
    ) -> V1RetrieveOrganizationsSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/organizations:search",
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
                    v1_retrieve_organizations_search_params.V1RetrieveOrganizationsSearchParams,
                ),
            ),
            cast_to=V1RetrieveOrganizationsSearchResponse,
        )

    async def retrieve_session_active(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/session:active",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_sessions_me(
        self,
        *,
        id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetCurrentSessionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/sessions:me",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"id": id}, v1_retrieve_sessions_me_params.V1RetrieveSessionsMeParams
                ),
            ),
            cast_to=GetCurrentSessionResponse,
        )

    async def retrieve_users_search(
        self,
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
    ) -> V1RetrieveUsersSearchResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/users:search",
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
                    v1_retrieve_users_search_params.V1RetrieveUsersSearchParams,
                ),
            ),
            cast_to=V1RetrieveUsersSearchResponse,
        )

    async def signup(
        self,
        *,
        company: str | Omit = omit,
        email: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1SignupResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/signup",
            body=await async_maybe_transform(
                {
                    "company": company,
                    "email": email,
                },
                v1_signup_params.V1SignupParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1SignupResponse,
        )

    async def tools_set_default(
        self,
        *,
        name: str | Omit = omit,
        schema_version: str | Omit = omit,
        tool_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> V1ToolsSetDefaultResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/tools:set_default",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "schema_version": schema_version,
                    "tool_version": tool_version,
                },
                v1_tools_set_default_params.V1ToolsSetDefaultParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1ToolsSetDefaultResponse,
        )

    async def update_roles_set_defaults(
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
            "/api/v1/roles:set_defaults",
            body=await async_maybe_transform(
                {
                    "default_creator": default_creator,
                    "default_creator_role": default_creator_role,
                    "default_member": default_member,
                    "default_member_role": default_member_role,
                },
                v1_update_roles_set_defaults_params.V1UpdateRolesSetDefaultsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDefaultRolesResponse,
        )

    async def update_workspaces_onboard(
        self,
        *,
        user_family_name: str | Omit = omit,
        user_given_name: str | Omit = omit,
        workspace_display_name: str | Omit = omit,
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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._patch(
            "/api/v1/workspaces:onboard",
            body=await async_maybe_transform(
                {
                    "user_family_name": user_family_name,
                    "user_given_name": user_given_name,
                    "workspace_display_name": workspace_display_name,
                },
                v1_update_workspaces_onboard_params.V1UpdateWorkspacesOnboardParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class V1ResourceWithRawResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

        self.retrieve = to_raw_response_wrapper(
            v1.retrieve,
        )
        self.auth_discovery = to_raw_response_wrapper(
            v1.auth_discovery,
        )
        self.auth_signup = to_raw_response_wrapper(
            v1.auth_signup,
        )
        self.connected_accounts_delete = to_raw_response_wrapper(
            v1.connected_accounts_delete,
        )
        self.execute_tool = to_raw_response_wrapper(
            v1.execute_tool,
        )
        self.fetch_bulk = to_raw_response_wrapper(
            v1.fetch_bulk,
        )
        self.retrieve_auth_customizations = to_raw_response_wrapper(
            v1.retrieve_auth_customizations,
        )
        self.retrieve_auth_features = to_raw_response_wrapper(
            v1.retrieve_auth_features,
        )
        self.retrieve_auth_organizations = to_raw_response_wrapper(
            v1.retrieve_auth_organizations,
        )
        self.retrieve_authmethods = to_raw_response_wrapper(
            v1.retrieve_authmethods,
        )
        self.retrieve_connected_accounts_search = to_raw_response_wrapper(
            v1.retrieve_connected_accounts_search,
        )
        self.retrieve_organizations_search = to_raw_response_wrapper(
            v1.retrieve_organizations_search,
        )
        self.retrieve_session_active = to_raw_response_wrapper(
            v1.retrieve_session_active,
        )
        self.retrieve_sessions_me = to_raw_response_wrapper(
            v1.retrieve_sessions_me,
        )
        self.retrieve_users_search = to_raw_response_wrapper(
            v1.retrieve_users_search,
        )
        self.signup = to_raw_response_wrapper(
            v1.signup,
        )
        self.tools_set_default = to_raw_response_wrapper(
            v1.tools_set_default,
        )
        self.update_roles_set_defaults = to_raw_response_wrapper(
            v1.update_roles_set_defaults,
        )
        self.update_workspaces_onboard = to_raw_response_wrapper(
            v1.update_workspaces_onboard,
        )

    @cached_property
    def auth(self) -> AuthResourceWithRawResponse:
        return AuthResourceWithRawResponse(self._v1.auth)

    @cached_property
    def billing(self) -> BillingResourceWithRawResponse:
        return BillingResourceWithRawResponse(self._v1.billing)

    @cached_property
    def clients(self) -> ClientsResourceWithRawResponse:
        return ClientsResourceWithRawResponse(self._v1.clients)

    @cached_property
    def connected_accounts(self) -> ConnectedAccountsResourceWithRawResponse:
        return ConnectedAccountsResourceWithRawResponse(self._v1.connected_accounts)

    @cached_property
    def connections(self) -> ConnectionsResourceWithRawResponse:
        return ConnectionsResourceWithRawResponse(self._v1.connections)

    @cached_property
    def directory_user_attributes(self) -> DirectoryUserAttributesResourceWithRawResponse:
        return DirectoryUserAttributesResourceWithRawResponse(self._v1.directory_user_attributes)

    @cached_property
    def environments(self) -> EnvironmentsResourceWithRawResponse:
        return EnvironmentsResourceWithRawResponse(self._v1.environments)

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._v1.events)

    @cached_property
    def features(self) -> FeaturesResourceWithRawResponse:
        return FeaturesResourceWithRawResponse(self._v1.features)

    @cached_property
    def invites(self) -> InvitesResourceWithRawResponse:
        return InvitesResourceWithRawResponse(self._v1.invites)

    @cached_property
    def logs(self) -> LogsResourceWithRawResponse:
        return LogsResourceWithRawResponse(self._v1.logs)

    @cached_property
    def mcp(self) -> McpResourceWithRawResponse:
        return McpResourceWithRawResponse(self._v1.mcp)

    @cached_property
    def members(self) -> MembersResourceWithRawResponse:
        return MembersResourceWithRawResponse(self._v1.members)

    @cached_property
    def members_this(self) -> MembersThisResourceWithRawResponse:
        return MembersThisResourceWithRawResponse(self._v1.members_this)

    @cached_property
    def memberships(self) -> MembershipsResourceWithRawResponse:
        return MembershipsResourceWithRawResponse(self._v1.memberships)

    @cached_property
    def oauth(self) -> OAuthResourceWithRawResponse:
        return OAuthResourceWithRawResponse(self._v1.oauth)

    @cached_property
    def organizations(self) -> OrganizationsResourceWithRawResponse:
        return OrganizationsResourceWithRawResponse(self._v1.organizations)

    @cached_property
    def passwordless(self) -> PasswordlessResourceWithRawResponse:
        return PasswordlessResourceWithRawResponse(self._v1.passwordless)

    @cached_property
    def permissions(self) -> PermissionsResourceWithRawResponse:
        return PermissionsResourceWithRawResponse(self._v1.permissions)

    @cached_property
    def providers(self) -> ProvidersResourceWithRawResponse:
        return ProvidersResourceWithRawResponse(self._v1.providers)

    @cached_property
    def resources(self) -> ResourcesResourceWithRawResponse:
        return ResourcesResourceWithRawResponse(self._v1.resources)

    @cached_property
    def roles(self) -> RolesResourceWithRawResponse:
        return RolesResourceWithRawResponse(self._v1.roles)

    @cached_property
    def scopes(self) -> ScopesResourceWithRawResponse:
        return ScopesResourceWithRawResponse(self._v1.scopes)

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._v1.sessions)

    @cached_property
    def sso_user_attributes(self) -> SSOUserAttributesResourceWithRawResponse:
        return SSOUserAttributesResourceWithRawResponse(self._v1.sso_user_attributes)

    @cached_property
    def tools(self) -> ToolsResourceWithRawResponse:
        return ToolsResourceWithRawResponse(self._v1.tools)

    @cached_property
    def totp(self) -> TotpResourceWithRawResponse:
        return TotpResourceWithRawResponse(self._v1.totp)

    @cached_property
    def user_profile_attributes(self) -> UserProfileAttributesResourceWithRawResponse:
        return UserProfileAttributesResourceWithRawResponse(self._v1.user_profile_attributes)

    @cached_property
    def webhooks(self) -> WebhooksResourceWithRawResponse:
        return WebhooksResourceWithRawResponse(self._v1.webhooks)

    @cached_property
    def workspaces(self) -> WorkspacesResourceWithRawResponse:
        return WorkspacesResourceWithRawResponse(self._v1.workspaces)

    @cached_property
    def workspaces_this(self) -> WorkspacesThisResourceWithRawResponse:
        return WorkspacesThisResourceWithRawResponse(self._v1.workspaces_this)

    @cached_property
    def email(self) -> EmailResourceWithRawResponse:
        return EmailResourceWithRawResponse(self._v1.email)

    @cached_property
    def user(self) -> UserResourceWithRawResponse:
        return UserResourceWithRawResponse(self._v1.user)


class AsyncV1ResourceWithRawResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

        self.retrieve = async_to_raw_response_wrapper(
            v1.retrieve,
        )
        self.auth_discovery = async_to_raw_response_wrapper(
            v1.auth_discovery,
        )
        self.auth_signup = async_to_raw_response_wrapper(
            v1.auth_signup,
        )
        self.connected_accounts_delete = async_to_raw_response_wrapper(
            v1.connected_accounts_delete,
        )
        self.execute_tool = async_to_raw_response_wrapper(
            v1.execute_tool,
        )
        self.fetch_bulk = async_to_raw_response_wrapper(
            v1.fetch_bulk,
        )
        self.retrieve_auth_customizations = async_to_raw_response_wrapper(
            v1.retrieve_auth_customizations,
        )
        self.retrieve_auth_features = async_to_raw_response_wrapper(
            v1.retrieve_auth_features,
        )
        self.retrieve_auth_organizations = async_to_raw_response_wrapper(
            v1.retrieve_auth_organizations,
        )
        self.retrieve_authmethods = async_to_raw_response_wrapper(
            v1.retrieve_authmethods,
        )
        self.retrieve_connected_accounts_search = async_to_raw_response_wrapper(
            v1.retrieve_connected_accounts_search,
        )
        self.retrieve_organizations_search = async_to_raw_response_wrapper(
            v1.retrieve_organizations_search,
        )
        self.retrieve_session_active = async_to_raw_response_wrapper(
            v1.retrieve_session_active,
        )
        self.retrieve_sessions_me = async_to_raw_response_wrapper(
            v1.retrieve_sessions_me,
        )
        self.retrieve_users_search = async_to_raw_response_wrapper(
            v1.retrieve_users_search,
        )
        self.signup = async_to_raw_response_wrapper(
            v1.signup,
        )
        self.tools_set_default = async_to_raw_response_wrapper(
            v1.tools_set_default,
        )
        self.update_roles_set_defaults = async_to_raw_response_wrapper(
            v1.update_roles_set_defaults,
        )
        self.update_workspaces_onboard = async_to_raw_response_wrapper(
            v1.update_workspaces_onboard,
        )

    @cached_property
    def auth(self) -> AsyncAuthResourceWithRawResponse:
        return AsyncAuthResourceWithRawResponse(self._v1.auth)

    @cached_property
    def billing(self) -> AsyncBillingResourceWithRawResponse:
        return AsyncBillingResourceWithRawResponse(self._v1.billing)

    @cached_property
    def clients(self) -> AsyncClientsResourceWithRawResponse:
        return AsyncClientsResourceWithRawResponse(self._v1.clients)

    @cached_property
    def connected_accounts(self) -> AsyncConnectedAccountsResourceWithRawResponse:
        return AsyncConnectedAccountsResourceWithRawResponse(self._v1.connected_accounts)

    @cached_property
    def connections(self) -> AsyncConnectionsResourceWithRawResponse:
        return AsyncConnectionsResourceWithRawResponse(self._v1.connections)

    @cached_property
    def directory_user_attributes(self) -> AsyncDirectoryUserAttributesResourceWithRawResponse:
        return AsyncDirectoryUserAttributesResourceWithRawResponse(self._v1.directory_user_attributes)

    @cached_property
    def environments(self) -> AsyncEnvironmentsResourceWithRawResponse:
        return AsyncEnvironmentsResourceWithRawResponse(self._v1.environments)

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._v1.events)

    @cached_property
    def features(self) -> AsyncFeaturesResourceWithRawResponse:
        return AsyncFeaturesResourceWithRawResponse(self._v1.features)

    @cached_property
    def invites(self) -> AsyncInvitesResourceWithRawResponse:
        return AsyncInvitesResourceWithRawResponse(self._v1.invites)

    @cached_property
    def logs(self) -> AsyncLogsResourceWithRawResponse:
        return AsyncLogsResourceWithRawResponse(self._v1.logs)

    @cached_property
    def mcp(self) -> AsyncMcpResourceWithRawResponse:
        return AsyncMcpResourceWithRawResponse(self._v1.mcp)

    @cached_property
    def members(self) -> AsyncMembersResourceWithRawResponse:
        return AsyncMembersResourceWithRawResponse(self._v1.members)

    @cached_property
    def members_this(self) -> AsyncMembersThisResourceWithRawResponse:
        return AsyncMembersThisResourceWithRawResponse(self._v1.members_this)

    @cached_property
    def memberships(self) -> AsyncMembershipsResourceWithRawResponse:
        return AsyncMembershipsResourceWithRawResponse(self._v1.memberships)

    @cached_property
    def oauth(self) -> AsyncOAuthResourceWithRawResponse:
        return AsyncOAuthResourceWithRawResponse(self._v1.oauth)

    @cached_property
    def organizations(self) -> AsyncOrganizationsResourceWithRawResponse:
        return AsyncOrganizationsResourceWithRawResponse(self._v1.organizations)

    @cached_property
    def passwordless(self) -> AsyncPasswordlessResourceWithRawResponse:
        return AsyncPasswordlessResourceWithRawResponse(self._v1.passwordless)

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithRawResponse:
        return AsyncPermissionsResourceWithRawResponse(self._v1.permissions)

    @cached_property
    def providers(self) -> AsyncProvidersResourceWithRawResponse:
        return AsyncProvidersResourceWithRawResponse(self._v1.providers)

    @cached_property
    def resources(self) -> AsyncResourcesResourceWithRawResponse:
        return AsyncResourcesResourceWithRawResponse(self._v1.resources)

    @cached_property
    def roles(self) -> AsyncRolesResourceWithRawResponse:
        return AsyncRolesResourceWithRawResponse(self._v1.roles)

    @cached_property
    def scopes(self) -> AsyncScopesResourceWithRawResponse:
        return AsyncScopesResourceWithRawResponse(self._v1.scopes)

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._v1.sessions)

    @cached_property
    def sso_user_attributes(self) -> AsyncSSOUserAttributesResourceWithRawResponse:
        return AsyncSSOUserAttributesResourceWithRawResponse(self._v1.sso_user_attributes)

    @cached_property
    def tools(self) -> AsyncToolsResourceWithRawResponse:
        return AsyncToolsResourceWithRawResponse(self._v1.tools)

    @cached_property
    def totp(self) -> AsyncTotpResourceWithRawResponse:
        return AsyncTotpResourceWithRawResponse(self._v1.totp)

    @cached_property
    def user_profile_attributes(self) -> AsyncUserProfileAttributesResourceWithRawResponse:
        return AsyncUserProfileAttributesResourceWithRawResponse(self._v1.user_profile_attributes)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResourceWithRawResponse:
        return AsyncWebhooksResourceWithRawResponse(self._v1.webhooks)

    @cached_property
    def workspaces(self) -> AsyncWorkspacesResourceWithRawResponse:
        return AsyncWorkspacesResourceWithRawResponse(self._v1.workspaces)

    @cached_property
    def workspaces_this(self) -> AsyncWorkspacesThisResourceWithRawResponse:
        return AsyncWorkspacesThisResourceWithRawResponse(self._v1.workspaces_this)

    @cached_property
    def email(self) -> AsyncEmailResourceWithRawResponse:
        return AsyncEmailResourceWithRawResponse(self._v1.email)

    @cached_property
    def user(self) -> AsyncUserResourceWithRawResponse:
        return AsyncUserResourceWithRawResponse(self._v1.user)


class V1ResourceWithStreamingResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

        self.retrieve = to_streamed_response_wrapper(
            v1.retrieve,
        )
        self.auth_discovery = to_streamed_response_wrapper(
            v1.auth_discovery,
        )
        self.auth_signup = to_streamed_response_wrapper(
            v1.auth_signup,
        )
        self.connected_accounts_delete = to_streamed_response_wrapper(
            v1.connected_accounts_delete,
        )
        self.execute_tool = to_streamed_response_wrapper(
            v1.execute_tool,
        )
        self.fetch_bulk = to_streamed_response_wrapper(
            v1.fetch_bulk,
        )
        self.retrieve_auth_customizations = to_streamed_response_wrapper(
            v1.retrieve_auth_customizations,
        )
        self.retrieve_auth_features = to_streamed_response_wrapper(
            v1.retrieve_auth_features,
        )
        self.retrieve_auth_organizations = to_streamed_response_wrapper(
            v1.retrieve_auth_organizations,
        )
        self.retrieve_authmethods = to_streamed_response_wrapper(
            v1.retrieve_authmethods,
        )
        self.retrieve_connected_accounts_search = to_streamed_response_wrapper(
            v1.retrieve_connected_accounts_search,
        )
        self.retrieve_organizations_search = to_streamed_response_wrapper(
            v1.retrieve_organizations_search,
        )
        self.retrieve_session_active = to_streamed_response_wrapper(
            v1.retrieve_session_active,
        )
        self.retrieve_sessions_me = to_streamed_response_wrapper(
            v1.retrieve_sessions_me,
        )
        self.retrieve_users_search = to_streamed_response_wrapper(
            v1.retrieve_users_search,
        )
        self.signup = to_streamed_response_wrapper(
            v1.signup,
        )
        self.tools_set_default = to_streamed_response_wrapper(
            v1.tools_set_default,
        )
        self.update_roles_set_defaults = to_streamed_response_wrapper(
            v1.update_roles_set_defaults,
        )
        self.update_workspaces_onboard = to_streamed_response_wrapper(
            v1.update_workspaces_onboard,
        )

    @cached_property
    def auth(self) -> AuthResourceWithStreamingResponse:
        return AuthResourceWithStreamingResponse(self._v1.auth)

    @cached_property
    def billing(self) -> BillingResourceWithStreamingResponse:
        return BillingResourceWithStreamingResponse(self._v1.billing)

    @cached_property
    def clients(self) -> ClientsResourceWithStreamingResponse:
        return ClientsResourceWithStreamingResponse(self._v1.clients)

    @cached_property
    def connected_accounts(self) -> ConnectedAccountsResourceWithStreamingResponse:
        return ConnectedAccountsResourceWithStreamingResponse(self._v1.connected_accounts)

    @cached_property
    def connections(self) -> ConnectionsResourceWithStreamingResponse:
        return ConnectionsResourceWithStreamingResponse(self._v1.connections)

    @cached_property
    def directory_user_attributes(self) -> DirectoryUserAttributesResourceWithStreamingResponse:
        return DirectoryUserAttributesResourceWithStreamingResponse(self._v1.directory_user_attributes)

    @cached_property
    def environments(self) -> EnvironmentsResourceWithStreamingResponse:
        return EnvironmentsResourceWithStreamingResponse(self._v1.environments)

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._v1.events)

    @cached_property
    def features(self) -> FeaturesResourceWithStreamingResponse:
        return FeaturesResourceWithStreamingResponse(self._v1.features)

    @cached_property
    def invites(self) -> InvitesResourceWithStreamingResponse:
        return InvitesResourceWithStreamingResponse(self._v1.invites)

    @cached_property
    def logs(self) -> LogsResourceWithStreamingResponse:
        return LogsResourceWithStreamingResponse(self._v1.logs)

    @cached_property
    def mcp(self) -> McpResourceWithStreamingResponse:
        return McpResourceWithStreamingResponse(self._v1.mcp)

    @cached_property
    def members(self) -> MembersResourceWithStreamingResponse:
        return MembersResourceWithStreamingResponse(self._v1.members)

    @cached_property
    def members_this(self) -> MembersThisResourceWithStreamingResponse:
        return MembersThisResourceWithStreamingResponse(self._v1.members_this)

    @cached_property
    def memberships(self) -> MembershipsResourceWithStreamingResponse:
        return MembershipsResourceWithStreamingResponse(self._v1.memberships)

    @cached_property
    def oauth(self) -> OAuthResourceWithStreamingResponse:
        return OAuthResourceWithStreamingResponse(self._v1.oauth)

    @cached_property
    def organizations(self) -> OrganizationsResourceWithStreamingResponse:
        return OrganizationsResourceWithStreamingResponse(self._v1.organizations)

    @cached_property
    def passwordless(self) -> PasswordlessResourceWithStreamingResponse:
        return PasswordlessResourceWithStreamingResponse(self._v1.passwordless)

    @cached_property
    def permissions(self) -> PermissionsResourceWithStreamingResponse:
        return PermissionsResourceWithStreamingResponse(self._v1.permissions)

    @cached_property
    def providers(self) -> ProvidersResourceWithStreamingResponse:
        return ProvidersResourceWithStreamingResponse(self._v1.providers)

    @cached_property
    def resources(self) -> ResourcesResourceWithStreamingResponse:
        return ResourcesResourceWithStreamingResponse(self._v1.resources)

    @cached_property
    def roles(self) -> RolesResourceWithStreamingResponse:
        return RolesResourceWithStreamingResponse(self._v1.roles)

    @cached_property
    def scopes(self) -> ScopesResourceWithStreamingResponse:
        return ScopesResourceWithStreamingResponse(self._v1.scopes)

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._v1.sessions)

    @cached_property
    def sso_user_attributes(self) -> SSOUserAttributesResourceWithStreamingResponse:
        return SSOUserAttributesResourceWithStreamingResponse(self._v1.sso_user_attributes)

    @cached_property
    def tools(self) -> ToolsResourceWithStreamingResponse:
        return ToolsResourceWithStreamingResponse(self._v1.tools)

    @cached_property
    def totp(self) -> TotpResourceWithStreamingResponse:
        return TotpResourceWithStreamingResponse(self._v1.totp)

    @cached_property
    def user_profile_attributes(self) -> UserProfileAttributesResourceWithStreamingResponse:
        return UserProfileAttributesResourceWithStreamingResponse(self._v1.user_profile_attributes)

    @cached_property
    def webhooks(self) -> WebhooksResourceWithStreamingResponse:
        return WebhooksResourceWithStreamingResponse(self._v1.webhooks)

    @cached_property
    def workspaces(self) -> WorkspacesResourceWithStreamingResponse:
        return WorkspacesResourceWithStreamingResponse(self._v1.workspaces)

    @cached_property
    def workspaces_this(self) -> WorkspacesThisResourceWithStreamingResponse:
        return WorkspacesThisResourceWithStreamingResponse(self._v1.workspaces_this)

    @cached_property
    def email(self) -> EmailResourceWithStreamingResponse:
        return EmailResourceWithStreamingResponse(self._v1.email)

    @cached_property
    def user(self) -> UserResourceWithStreamingResponse:
        return UserResourceWithStreamingResponse(self._v1.user)


class AsyncV1ResourceWithStreamingResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

        self.retrieve = async_to_streamed_response_wrapper(
            v1.retrieve,
        )
        self.auth_discovery = async_to_streamed_response_wrapper(
            v1.auth_discovery,
        )
        self.auth_signup = async_to_streamed_response_wrapper(
            v1.auth_signup,
        )
        self.connected_accounts_delete = async_to_streamed_response_wrapper(
            v1.connected_accounts_delete,
        )
        self.execute_tool = async_to_streamed_response_wrapper(
            v1.execute_tool,
        )
        self.fetch_bulk = async_to_streamed_response_wrapper(
            v1.fetch_bulk,
        )
        self.retrieve_auth_customizations = async_to_streamed_response_wrapper(
            v1.retrieve_auth_customizations,
        )
        self.retrieve_auth_features = async_to_streamed_response_wrapper(
            v1.retrieve_auth_features,
        )
        self.retrieve_auth_organizations = async_to_streamed_response_wrapper(
            v1.retrieve_auth_organizations,
        )
        self.retrieve_authmethods = async_to_streamed_response_wrapper(
            v1.retrieve_authmethods,
        )
        self.retrieve_connected_accounts_search = async_to_streamed_response_wrapper(
            v1.retrieve_connected_accounts_search,
        )
        self.retrieve_organizations_search = async_to_streamed_response_wrapper(
            v1.retrieve_organizations_search,
        )
        self.retrieve_session_active = async_to_streamed_response_wrapper(
            v1.retrieve_session_active,
        )
        self.retrieve_sessions_me = async_to_streamed_response_wrapper(
            v1.retrieve_sessions_me,
        )
        self.retrieve_users_search = async_to_streamed_response_wrapper(
            v1.retrieve_users_search,
        )
        self.signup = async_to_streamed_response_wrapper(
            v1.signup,
        )
        self.tools_set_default = async_to_streamed_response_wrapper(
            v1.tools_set_default,
        )
        self.update_roles_set_defaults = async_to_streamed_response_wrapper(
            v1.update_roles_set_defaults,
        )
        self.update_workspaces_onboard = async_to_streamed_response_wrapper(
            v1.update_workspaces_onboard,
        )

    @cached_property
    def auth(self) -> AsyncAuthResourceWithStreamingResponse:
        return AsyncAuthResourceWithStreamingResponse(self._v1.auth)

    @cached_property
    def billing(self) -> AsyncBillingResourceWithStreamingResponse:
        return AsyncBillingResourceWithStreamingResponse(self._v1.billing)

    @cached_property
    def clients(self) -> AsyncClientsResourceWithStreamingResponse:
        return AsyncClientsResourceWithStreamingResponse(self._v1.clients)

    @cached_property
    def connected_accounts(self) -> AsyncConnectedAccountsResourceWithStreamingResponse:
        return AsyncConnectedAccountsResourceWithStreamingResponse(self._v1.connected_accounts)

    @cached_property
    def connections(self) -> AsyncConnectionsResourceWithStreamingResponse:
        return AsyncConnectionsResourceWithStreamingResponse(self._v1.connections)

    @cached_property
    def directory_user_attributes(self) -> AsyncDirectoryUserAttributesResourceWithStreamingResponse:
        return AsyncDirectoryUserAttributesResourceWithStreamingResponse(self._v1.directory_user_attributes)

    @cached_property
    def environments(self) -> AsyncEnvironmentsResourceWithStreamingResponse:
        return AsyncEnvironmentsResourceWithStreamingResponse(self._v1.environments)

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._v1.events)

    @cached_property
    def features(self) -> AsyncFeaturesResourceWithStreamingResponse:
        return AsyncFeaturesResourceWithStreamingResponse(self._v1.features)

    @cached_property
    def invites(self) -> AsyncInvitesResourceWithStreamingResponse:
        return AsyncInvitesResourceWithStreamingResponse(self._v1.invites)

    @cached_property
    def logs(self) -> AsyncLogsResourceWithStreamingResponse:
        return AsyncLogsResourceWithStreamingResponse(self._v1.logs)

    @cached_property
    def mcp(self) -> AsyncMcpResourceWithStreamingResponse:
        return AsyncMcpResourceWithStreamingResponse(self._v1.mcp)

    @cached_property
    def members(self) -> AsyncMembersResourceWithStreamingResponse:
        return AsyncMembersResourceWithStreamingResponse(self._v1.members)

    @cached_property
    def members_this(self) -> AsyncMembersThisResourceWithStreamingResponse:
        return AsyncMembersThisResourceWithStreamingResponse(self._v1.members_this)

    @cached_property
    def memberships(self) -> AsyncMembershipsResourceWithStreamingResponse:
        return AsyncMembershipsResourceWithStreamingResponse(self._v1.memberships)

    @cached_property
    def oauth(self) -> AsyncOAuthResourceWithStreamingResponse:
        return AsyncOAuthResourceWithStreamingResponse(self._v1.oauth)

    @cached_property
    def organizations(self) -> AsyncOrganizationsResourceWithStreamingResponse:
        return AsyncOrganizationsResourceWithStreamingResponse(self._v1.organizations)

    @cached_property
    def passwordless(self) -> AsyncPasswordlessResourceWithStreamingResponse:
        return AsyncPasswordlessResourceWithStreamingResponse(self._v1.passwordless)

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithStreamingResponse:
        return AsyncPermissionsResourceWithStreamingResponse(self._v1.permissions)

    @cached_property
    def providers(self) -> AsyncProvidersResourceWithStreamingResponse:
        return AsyncProvidersResourceWithStreamingResponse(self._v1.providers)

    @cached_property
    def resources(self) -> AsyncResourcesResourceWithStreamingResponse:
        return AsyncResourcesResourceWithStreamingResponse(self._v1.resources)

    @cached_property
    def roles(self) -> AsyncRolesResourceWithStreamingResponse:
        return AsyncRolesResourceWithStreamingResponse(self._v1.roles)

    @cached_property
    def scopes(self) -> AsyncScopesResourceWithStreamingResponse:
        return AsyncScopesResourceWithStreamingResponse(self._v1.scopes)

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._v1.sessions)

    @cached_property
    def sso_user_attributes(self) -> AsyncSSOUserAttributesResourceWithStreamingResponse:
        return AsyncSSOUserAttributesResourceWithStreamingResponse(self._v1.sso_user_attributes)

    @cached_property
    def tools(self) -> AsyncToolsResourceWithStreamingResponse:
        return AsyncToolsResourceWithStreamingResponse(self._v1.tools)

    @cached_property
    def totp(self) -> AsyncTotpResourceWithStreamingResponse:
        return AsyncTotpResourceWithStreamingResponse(self._v1.totp)

    @cached_property
    def user_profile_attributes(self) -> AsyncUserProfileAttributesResourceWithStreamingResponse:
        return AsyncUserProfileAttributesResourceWithStreamingResponse(self._v1.user_profile_attributes)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResourceWithStreamingResponse:
        return AsyncWebhooksResourceWithStreamingResponse(self._v1.webhooks)

    @cached_property
    def workspaces(self) -> AsyncWorkspacesResourceWithStreamingResponse:
        return AsyncWorkspacesResourceWithStreamingResponse(self._v1.workspaces)

    @cached_property
    def workspaces_this(self) -> AsyncWorkspacesThisResourceWithStreamingResponse:
        return AsyncWorkspacesThisResourceWithStreamingResponse(self._v1.workspaces_this)

    @cached_property
    def email(self) -> AsyncEmailResourceWithStreamingResponse:
        return AsyncEmailResourceWithStreamingResponse(self._v1.email)

    @cached_property
    def user(self) -> AsyncUserResourceWithStreamingResponse:
        return AsyncUserResourceWithStreamingResponse(self._v1.user)
