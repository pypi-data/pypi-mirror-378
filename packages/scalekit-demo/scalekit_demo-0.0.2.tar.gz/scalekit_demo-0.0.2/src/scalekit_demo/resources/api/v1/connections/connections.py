# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .auth_requests import (
    AuthRequestsResource,
    AsyncAuthRequestsResource,
    AuthRequestsResourceWithRawResponse,
    AsyncAuthRequestsResourceWithRawResponse,
    AuthRequestsResourceWithStreamingResponse,
    AsyncAuthRequestsResourceWithStreamingResponse,
)
from ....._base_client import make_request_options
from .....types.api.v1 import (
    connection_list_params,
    connection_create_params,
    connection_update_params,
    connection_retrieve_app_params,
)
from .....types.api.v1.connection_list_response import ConnectionListResponse
from .....types.api.v1.static_auth_config_param import StaticAuthConfigParam
from .....types.api.v1.create_connection_response import CreateConnectionResponse
from .....types.api.v1.password_less_config_param import PasswordLessConfigParam
from .....types.api.v1.toggle_connection_response import ToggleConnectionResponse
from .....types.api.v1.update_connection_response import UpdateConnectionResponse
from .....types.api.v1.connection_retrieve_response import ConnectionRetrieveResponse
from .....types.api.v1.oidc_connection_config_param import OidcConnectionConfigParam
from .....types.api.v1.oauth_connection_config_param import OAuthConnectionConfigParam
from .....types.api.v1.connection_retrieve_app_response import ConnectionRetrieveAppResponse

__all__ = ["ConnectionsResource", "AsyncConnectionsResource"]


class ConnectionsResource(SyncAPIResource):
    @cached_property
    def auth_requests(self) -> AuthRequestsResource:
        return AuthRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ConnectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return ConnectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConnectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return ConnectionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        flags: connection_create_params.Flags | Omit = omit,
        key_id: str | Omit = omit,
        provider: int | Omit = omit,
        provider_key: str | Omit = omit,
        type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CreateConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/connections",
            body=maybe_transform(
                {
                    "key_id": key_id,
                    "provider": provider,
                    "provider_key": provider_key,
                    "type": type,
                },
                connection_create_params.ConnectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"flags": flags}, connection_create_params.ConnectionCreateParams),
            ),
            cast_to=CreateConnectionResponse,
        )

    def retrieve(
        self,
        test_request_id: str,
        *,
        connection_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        if not test_request_id:
            raise ValueError(f"Expected a non-empty value for `test_request_id` but received {test_request_id!r}")
        return self._get(
            f"/api/v1/connections/{connection_id}/test-requests/{test_request_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionRetrieveResponse,
        )

    def update(
        self,
        connection_id: str,
        *,
        attribute_mapping: Dict[str, str] | Omit = omit,
        configuration_type: int | Omit = omit,
        debug_enabled: bool | Omit = omit,
        key_id: str | Omit = omit,
        oauth_config: OAuthConnectionConfigParam | Omit = omit,
        oidc_config: OidcConnectionConfigParam | Omit = omit,
        passwordless_config: PasswordLessConfigParam | Omit = omit,
        provider: int | Omit = omit,
        provider_key: str | Omit = omit,
        saml_config: connection_update_params.SAMLConfig | Omit = omit,
        static_config: StaticAuthConfigParam | Omit = omit,
        type: int | Omit = omit,
        ui_button_title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._patch(
            f"/api/v1/connections/{connection_id}",
            body=maybe_transform(
                {
                    "attribute_mapping": attribute_mapping,
                    "configuration_type": configuration_type,
                    "debug_enabled": debug_enabled,
                    "key_id": key_id,
                    "oauth_config": oauth_config,
                    "oidc_config": oidc_config,
                    "passwordless_config": passwordless_config,
                    "provider": provider,
                    "provider_key": provider_key,
                    "saml_config": saml_config,
                    "static_config": static_config,
                    "type": type,
                    "ui_button_title": ui_button_title,
                },
                connection_update_params.ConnectionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateConnectionResponse,
        )

    def list(
        self,
        *,
        domain: str | Omit = omit,
        include: str | Omit = omit,
        organization_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/connections",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain": domain,
                        "include": include,
                        "organization_id": organization_id,
                    },
                    connection_list_params.ConnectionListParams,
                ),
            ),
            cast_to=ConnectionListResponse,
        )

    def delete(
        self,
        connection_id: str,
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
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/connections/{connection_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_app(
        self,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        provider: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionRetrieveAppResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/connections/app",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                        "provider": provider,
                    },
                    connection_retrieve_app_params.ConnectionRetrieveAppParams,
                ),
            ),
            cast_to=ConnectionRetrieveAppResponse,
        )

    def update_connection_id_disable(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._patch(
            f"/api/v1/connections/{connection_id}:disable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleConnectionResponse,
        )

    def update_connection_id_enable(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._patch(
            f"/api/v1/connections/{connection_id}:enable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleConnectionResponse,
        )


class AsyncConnectionsResource(AsyncAPIResource):
    @cached_property
    def auth_requests(self) -> AsyncAuthRequestsResource:
        return AsyncAuthRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncConnectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConnectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConnectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncConnectionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        flags: connection_create_params.Flags | Omit = omit,
        key_id: str | Omit = omit,
        provider: int | Omit = omit,
        provider_key: str | Omit = omit,
        type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CreateConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/connections",
            body=await async_maybe_transform(
                {
                    "key_id": key_id,
                    "provider": provider,
                    "provider_key": provider_key,
                    "type": type,
                },
                connection_create_params.ConnectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"flags": flags}, connection_create_params.ConnectionCreateParams),
            ),
            cast_to=CreateConnectionResponse,
        )

    async def retrieve(
        self,
        test_request_id: str,
        *,
        connection_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        if not test_request_id:
            raise ValueError(f"Expected a non-empty value for `test_request_id` but received {test_request_id!r}")
        return await self._get(
            f"/api/v1/connections/{connection_id}/test-requests/{test_request_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionRetrieveResponse,
        )

    async def update(
        self,
        connection_id: str,
        *,
        attribute_mapping: Dict[str, str] | Omit = omit,
        configuration_type: int | Omit = omit,
        debug_enabled: bool | Omit = omit,
        key_id: str | Omit = omit,
        oauth_config: OAuthConnectionConfigParam | Omit = omit,
        oidc_config: OidcConnectionConfigParam | Omit = omit,
        passwordless_config: PasswordLessConfigParam | Omit = omit,
        provider: int | Omit = omit,
        provider_key: str | Omit = omit,
        saml_config: connection_update_params.SAMLConfig | Omit = omit,
        static_config: StaticAuthConfigParam | Omit = omit,
        type: int | Omit = omit,
        ui_button_title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._patch(
            f"/api/v1/connections/{connection_id}",
            body=await async_maybe_transform(
                {
                    "attribute_mapping": attribute_mapping,
                    "configuration_type": configuration_type,
                    "debug_enabled": debug_enabled,
                    "key_id": key_id,
                    "oauth_config": oauth_config,
                    "oidc_config": oidc_config,
                    "passwordless_config": passwordless_config,
                    "provider": provider,
                    "provider_key": provider_key,
                    "saml_config": saml_config,
                    "static_config": static_config,
                    "type": type,
                    "ui_button_title": ui_button_title,
                },
                connection_update_params.ConnectionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateConnectionResponse,
        )

    async def list(
        self,
        *,
        domain: str | Omit = omit,
        include: str | Omit = omit,
        organization_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/connections",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain": domain,
                        "include": include,
                        "organization_id": organization_id,
                    },
                    connection_list_params.ConnectionListParams,
                ),
            ),
            cast_to=ConnectionListResponse,
        )

    async def delete(
        self,
        connection_id: str,
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
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/connections/{connection_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_app(
        self,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        provider: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionRetrieveAppResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/connections/app",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                        "provider": provider,
                    },
                    connection_retrieve_app_params.ConnectionRetrieveAppParams,
                ),
            ),
            cast_to=ConnectionRetrieveAppResponse,
        )

    async def update_connection_id_disable(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._patch(
            f"/api/v1/connections/{connection_id}:disable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleConnectionResponse,
        )

    async def update_connection_id_enable(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ToggleConnectionResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._patch(
            f"/api/v1/connections/{connection_id}:enable",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ToggleConnectionResponse,
        )


class ConnectionsResourceWithRawResponse:
    def __init__(self, connections: ConnectionsResource) -> None:
        self._connections = connections

        self.create = to_raw_response_wrapper(
            connections.create,
        )
        self.retrieve = to_raw_response_wrapper(
            connections.retrieve,
        )
        self.update = to_raw_response_wrapper(
            connections.update,
        )
        self.list = to_raw_response_wrapper(
            connections.list,
        )
        self.delete = to_raw_response_wrapper(
            connections.delete,
        )
        self.retrieve_app = to_raw_response_wrapper(
            connections.retrieve_app,
        )
        self.update_connection_id_disable = to_raw_response_wrapper(
            connections.update_connection_id_disable,
        )
        self.update_connection_id_enable = to_raw_response_wrapper(
            connections.update_connection_id_enable,
        )

    @cached_property
    def auth_requests(self) -> AuthRequestsResourceWithRawResponse:
        return AuthRequestsResourceWithRawResponse(self._connections.auth_requests)


class AsyncConnectionsResourceWithRawResponse:
    def __init__(self, connections: AsyncConnectionsResource) -> None:
        self._connections = connections

        self.create = async_to_raw_response_wrapper(
            connections.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            connections.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            connections.update,
        )
        self.list = async_to_raw_response_wrapper(
            connections.list,
        )
        self.delete = async_to_raw_response_wrapper(
            connections.delete,
        )
        self.retrieve_app = async_to_raw_response_wrapper(
            connections.retrieve_app,
        )
        self.update_connection_id_disable = async_to_raw_response_wrapper(
            connections.update_connection_id_disable,
        )
        self.update_connection_id_enable = async_to_raw_response_wrapper(
            connections.update_connection_id_enable,
        )

    @cached_property
    def auth_requests(self) -> AsyncAuthRequestsResourceWithRawResponse:
        return AsyncAuthRequestsResourceWithRawResponse(self._connections.auth_requests)


class ConnectionsResourceWithStreamingResponse:
    def __init__(self, connections: ConnectionsResource) -> None:
        self._connections = connections

        self.create = to_streamed_response_wrapper(
            connections.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            connections.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            connections.update,
        )
        self.list = to_streamed_response_wrapper(
            connections.list,
        )
        self.delete = to_streamed_response_wrapper(
            connections.delete,
        )
        self.retrieve_app = to_streamed_response_wrapper(
            connections.retrieve_app,
        )
        self.update_connection_id_disable = to_streamed_response_wrapper(
            connections.update_connection_id_disable,
        )
        self.update_connection_id_enable = to_streamed_response_wrapper(
            connections.update_connection_id_enable,
        )

    @cached_property
    def auth_requests(self) -> AuthRequestsResourceWithStreamingResponse:
        return AuthRequestsResourceWithStreamingResponse(self._connections.auth_requests)


class AsyncConnectionsResourceWithStreamingResponse:
    def __init__(self, connections: AsyncConnectionsResource) -> None:
        self._connections = connections

        self.create = async_to_streamed_response_wrapper(
            connections.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            connections.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            connections.update,
        )
        self.list = async_to_streamed_response_wrapper(
            connections.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            connections.delete,
        )
        self.retrieve_app = async_to_streamed_response_wrapper(
            connections.retrieve_app,
        )
        self.update_connection_id_disable = async_to_streamed_response_wrapper(
            connections.update_connection_id_disable,
        )
        self.update_connection_id_enable = async_to_streamed_response_wrapper(
            connections.update_connection_id_enable,
        )

    @cached_property
    def auth_requests(self) -> AsyncAuthRequestsResourceWithStreamingResponse:
        return AsyncAuthRequestsResourceWithStreamingResponse(self._connections.auth_requests)
