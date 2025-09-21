# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .clients import (
    ClientsResource,
    AsyncClientsResource,
    ClientsResourceWithRawResponse,
    AsyncClientsResourceWithRawResponse,
    ClientsResourceWithStreamingResponse,
    AsyncClientsResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1 import (
    resource_list_params,
    resource_create_params,
    resource_update_params,
    resource_clients_register_params,
)
from .....types.api.v1.get_resource_response import GetResourceResponse
from .....types.api.v1.resource_list_response import ResourceListResponse
from .....types.api.v1.resource_create_response import ResourceCreateResponse
from .....types.api.v1.resource_update_response import ResourceUpdateResponse
from .....types.api.v1.resource_clients_register_response import ResourceClientsRegisterResponse

__all__ = ["ResourcesResource", "AsyncResourcesResource"]


class ResourcesResource(SyncAPIResource):
    @cached_property
    def clients(self) -> ClientsResource:
        return ClientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ResourcesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return ResourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResourcesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return ResourcesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        access_token_expiry: str | Omit = omit,
        description: str | Omit = omit,
        disable_dynamic_client_registration: bool | Omit = omit,
        logo_uri: str | Omit = omit,
        name: str | Omit = omit,
        provider: str | Omit = omit,
        refresh_token_expiry: str | Omit = omit,
        resource_id: str | Omit = omit,
        resource_type: int | Omit = omit,
        resource_uri: str | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/resources",
            body=maybe_transform(
                {
                    "access_token_expiry": access_token_expiry,
                    "description": description,
                    "disable_dynamic_client_registration": disable_dynamic_client_registration,
                    "logo_uri": logo_uri,
                    "name": name,
                    "provider": provider,
                    "refresh_token_expiry": refresh_token_expiry,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    "resource_uri": resource_uri,
                    "scopes": scopes,
                },
                resource_create_params.ResourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResourceCreateResponse,
        )

    def retrieve(
        self,
        resource_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetResourceResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return self._get(
            f"/api/v1/resources/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetResourceResponse,
        )

    def update(
        self,
        path_resource_id: str,
        *,
        update_mask: str | Omit = omit,
        access_token_expiry: str | Omit = omit,
        description: str | Omit = omit,
        disable_dynamic_client_registration: bool | Omit = omit,
        logo_uri: str | Omit = omit,
        name: str | Omit = omit,
        provider: str | Omit = omit,
        refresh_token_expiry: str | Omit = omit,
        body_resource_id: str | Omit = omit,
        resource_uri: str | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceUpdateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_resource_id:
            raise ValueError(f"Expected a non-empty value for `path_resource_id` but received {path_resource_id!r}")
        return self._patch(
            f"/api/v1/resources/{path_resource_id}",
            body=maybe_transform(
                {
                    "access_token_expiry": access_token_expiry,
                    "description": description,
                    "disable_dynamic_client_registration": disable_dynamic_client_registration,
                    "logo_uri": logo_uri,
                    "name": name,
                    "provider": provider,
                    "refresh_token_expiry": refresh_token_expiry,
                    "body_resource_id": body_resource_id,
                    "resource_uri": resource_uri,
                    "scopes": scopes,
                },
                resource_update_params.ResourceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"update_mask": update_mask}, resource_update_params.ResourceUpdateParams),
            ),
            cast_to=ResourceUpdateResponse,
        )

    def list(
        self,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        resource_type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                        "resource_type": resource_type,
                    },
                    resource_list_params.ResourceListParams,
                ),
            ),
            cast_to=ResourceListResponse,
        )

    def delete(
        self,
        resource_id: str,
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
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/resources/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def clients_register(
        self,
        res_id: str,
        *,
        client_name: str | Omit = omit,
        client_uri: str | Omit = omit,
        description: str | Omit = omit,
        logo_uri: str | Omit = omit,
        policy_uri: str | Omit = omit,
        redirect_uris: SequenceNotStr[str] | Omit = omit,
        scope: str | Omit = omit,
        tos_uri: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceClientsRegisterResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not res_id:
            raise ValueError(f"Expected a non-empty value for `res_id` but received {res_id!r}")
        return self._post(
            f"/api/v1/resources/{res_id}/clients:register",
            body=maybe_transform(
                {
                    "client_name": client_name,
                    "client_uri": client_uri,
                    "description": description,
                    "logo_uri": logo_uri,
                    "policy_uri": policy_uri,
                    "redirect_uris": redirect_uris,
                    "scope": scope,
                    "tos_uri": tos_uri,
                },
                resource_clients_register_params.ResourceClientsRegisterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResourceClientsRegisterResponse,
        )

    def update_provider_delete(
        self,
        resource_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetResourceResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return self._put(
            f"/api/v1/resources/{resource_id}/provider:delete",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetResourceResponse,
        )


class AsyncResourcesResource(AsyncAPIResource):
    @cached_property
    def clients(self) -> AsyncClientsResource:
        return AsyncClientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncResourcesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncResourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResourcesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncResourcesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        access_token_expiry: str | Omit = omit,
        description: str | Omit = omit,
        disable_dynamic_client_registration: bool | Omit = omit,
        logo_uri: str | Omit = omit,
        name: str | Omit = omit,
        provider: str | Omit = omit,
        refresh_token_expiry: str | Omit = omit,
        resource_id: str | Omit = omit,
        resource_type: int | Omit = omit,
        resource_uri: str | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/resources",
            body=await async_maybe_transform(
                {
                    "access_token_expiry": access_token_expiry,
                    "description": description,
                    "disable_dynamic_client_registration": disable_dynamic_client_registration,
                    "logo_uri": logo_uri,
                    "name": name,
                    "provider": provider,
                    "refresh_token_expiry": refresh_token_expiry,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    "resource_uri": resource_uri,
                    "scopes": scopes,
                },
                resource_create_params.ResourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResourceCreateResponse,
        )

    async def retrieve(
        self,
        resource_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetResourceResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return await self._get(
            f"/api/v1/resources/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetResourceResponse,
        )

    async def update(
        self,
        path_resource_id: str,
        *,
        update_mask: str | Omit = omit,
        access_token_expiry: str | Omit = omit,
        description: str | Omit = omit,
        disable_dynamic_client_registration: bool | Omit = omit,
        logo_uri: str | Omit = omit,
        name: str | Omit = omit,
        provider: str | Omit = omit,
        refresh_token_expiry: str | Omit = omit,
        body_resource_id: str | Omit = omit,
        resource_uri: str | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceUpdateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_resource_id:
            raise ValueError(f"Expected a non-empty value for `path_resource_id` but received {path_resource_id!r}")
        return await self._patch(
            f"/api/v1/resources/{path_resource_id}",
            body=await async_maybe_transform(
                {
                    "access_token_expiry": access_token_expiry,
                    "description": description,
                    "disable_dynamic_client_registration": disable_dynamic_client_registration,
                    "logo_uri": logo_uri,
                    "name": name,
                    "provider": provider,
                    "refresh_token_expiry": refresh_token_expiry,
                    "body_resource_id": body_resource_id,
                    "resource_uri": resource_uri,
                    "scopes": scopes,
                },
                resource_update_params.ResourceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, resource_update_params.ResourceUpdateParams
                ),
            ),
            cast_to=ResourceUpdateResponse,
        )

    async def list(
        self,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        resource_type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                        "resource_type": resource_type,
                    },
                    resource_list_params.ResourceListParams,
                ),
            ),
            cast_to=ResourceListResponse,
        )

    async def delete(
        self,
        resource_id: str,
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
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/resources/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def clients_register(
        self,
        res_id: str,
        *,
        client_name: str | Omit = omit,
        client_uri: str | Omit = omit,
        description: str | Omit = omit,
        logo_uri: str | Omit = omit,
        policy_uri: str | Omit = omit,
        redirect_uris: SequenceNotStr[str] | Omit = omit,
        scope: str | Omit = omit,
        tos_uri: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ResourceClientsRegisterResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not res_id:
            raise ValueError(f"Expected a non-empty value for `res_id` but received {res_id!r}")
        return await self._post(
            f"/api/v1/resources/{res_id}/clients:register",
            body=await async_maybe_transform(
                {
                    "client_name": client_name,
                    "client_uri": client_uri,
                    "description": description,
                    "logo_uri": logo_uri,
                    "policy_uri": policy_uri,
                    "redirect_uris": redirect_uris,
                    "scope": scope,
                    "tos_uri": tos_uri,
                },
                resource_clients_register_params.ResourceClientsRegisterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResourceClientsRegisterResponse,
        )

    async def update_provider_delete(
        self,
        resource_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetResourceResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return await self._put(
            f"/api/v1/resources/{resource_id}/provider:delete",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetResourceResponse,
        )


class ResourcesResourceWithRawResponse:
    def __init__(self, resources: ResourcesResource) -> None:
        self._resources = resources

        self.create = to_raw_response_wrapper(
            resources.create,
        )
        self.retrieve = to_raw_response_wrapper(
            resources.retrieve,
        )
        self.update = to_raw_response_wrapper(
            resources.update,
        )
        self.list = to_raw_response_wrapper(
            resources.list,
        )
        self.delete = to_raw_response_wrapper(
            resources.delete,
        )
        self.clients_register = to_raw_response_wrapper(
            resources.clients_register,
        )
        self.update_provider_delete = to_raw_response_wrapper(
            resources.update_provider_delete,
        )

    @cached_property
    def clients(self) -> ClientsResourceWithRawResponse:
        return ClientsResourceWithRawResponse(self._resources.clients)


class AsyncResourcesResourceWithRawResponse:
    def __init__(self, resources: AsyncResourcesResource) -> None:
        self._resources = resources

        self.create = async_to_raw_response_wrapper(
            resources.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            resources.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            resources.update,
        )
        self.list = async_to_raw_response_wrapper(
            resources.list,
        )
        self.delete = async_to_raw_response_wrapper(
            resources.delete,
        )
        self.clients_register = async_to_raw_response_wrapper(
            resources.clients_register,
        )
        self.update_provider_delete = async_to_raw_response_wrapper(
            resources.update_provider_delete,
        )

    @cached_property
    def clients(self) -> AsyncClientsResourceWithRawResponse:
        return AsyncClientsResourceWithRawResponse(self._resources.clients)


class ResourcesResourceWithStreamingResponse:
    def __init__(self, resources: ResourcesResource) -> None:
        self._resources = resources

        self.create = to_streamed_response_wrapper(
            resources.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            resources.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            resources.update,
        )
        self.list = to_streamed_response_wrapper(
            resources.list,
        )
        self.delete = to_streamed_response_wrapper(
            resources.delete,
        )
        self.clients_register = to_streamed_response_wrapper(
            resources.clients_register,
        )
        self.update_provider_delete = to_streamed_response_wrapper(
            resources.update_provider_delete,
        )

    @cached_property
    def clients(self) -> ClientsResourceWithStreamingResponse:
        return ClientsResourceWithStreamingResponse(self._resources.clients)


class AsyncResourcesResourceWithStreamingResponse:
    def __init__(self, resources: AsyncResourcesResource) -> None:
        self._resources = resources

        self.create = async_to_streamed_response_wrapper(
            resources.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            resources.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            resources.update,
        )
        self.list = async_to_streamed_response_wrapper(
            resources.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            resources.delete,
        )
        self.clients_register = async_to_streamed_response_wrapper(
            resources.clients_register,
        )
        self.update_provider_delete = async_to_streamed_response_wrapper(
            resources.update_provider_delete,
        )

    @cached_property
    def clients(self) -> AsyncClientsResourceWithStreamingResponse:
        return AsyncClientsResourceWithStreamingResponse(self._resources.clients)
