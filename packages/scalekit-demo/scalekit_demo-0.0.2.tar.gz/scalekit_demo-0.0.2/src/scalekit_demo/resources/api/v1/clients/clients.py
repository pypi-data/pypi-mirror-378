# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .secrets import (
    SecretsResource,
    AsyncSecretsResource,
    SecretsResourceWithRawResponse,
    AsyncSecretsResourceWithRawResponse,
    SecretsResourceWithStreamingResponse,
    AsyncSecretsResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from .....types.api.v1 import client_list_params, client_update_params
from .....types.api.v1.client_list_response import ClientListResponse
from .....types.api.v1.client_update_response import ClientUpdateResponse
from .....types.api.v1.client_retrieve_response import ClientRetrieveResponse

__all__ = ["ClientsResource", "AsyncClientsResource"]


class ClientsResource(SyncAPIResource):
    @cached_property
    def secrets(self) -> SecretsResource:
        return SecretsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ClientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return ClientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return ClientsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        client_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClientRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not client_id:
            raise ValueError(f"Expected a non-empty value for `client_id` but received {client_id!r}")
        return self._get(
            f"/api/v1/clients/{client_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClientRetrieveResponse,
        )

    def update(
        self,
        client_id: str,
        *,
        mask: str | Omit = omit,
        back_channel_logout_uris: SequenceNotStr[str] | Omit = omit,
        default_redirect_uri: str | Omit = omit,
        initiate_login_uri: str | Omit = omit,
        post_login_uris: SequenceNotStr[str] | Omit = omit,
        post_logout_redirect_uris: SequenceNotStr[str] | Omit = omit,
        redirect_uris: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClientUpdateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not client_id:
            raise ValueError(f"Expected a non-empty value for `client_id` but received {client_id!r}")
        return self._patch(
            f"/api/v1/clients/{client_id}",
            body=maybe_transform(
                {
                    "back_channel_logout_uris": back_channel_logout_uris,
                    "default_redirect_uri": default_redirect_uri,
                    "initiate_login_uri": initiate_login_uri,
                    "post_login_uris": post_login_uris,
                    "post_logout_redirect_uris": post_logout_redirect_uris,
                    "redirect_uris": redirect_uris,
                },
                client_update_params.ClientUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"mask": mask}, client_update_params.ClientUpdateParams),
            ),
            cast_to=ClientUpdateResponse,
        )

    def list(
        self,
        *,
        include_plain_secret: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClientListResponse:
        """
        Args:
          include_plain_secret: Controls whether plain secret values are included in the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/clients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"include_plain_secret": include_plain_secret}, client_list_params.ClientListParams
                ),
            ),
            cast_to=ClientListResponse,
        )


class AsyncClientsResource(AsyncAPIResource):
    @cached_property
    def secrets(self) -> AsyncSecretsResource:
        return AsyncSecretsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncClientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncClientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncClientsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        client_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClientRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not client_id:
            raise ValueError(f"Expected a non-empty value for `client_id` but received {client_id!r}")
        return await self._get(
            f"/api/v1/clients/{client_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClientRetrieveResponse,
        )

    async def update(
        self,
        client_id: str,
        *,
        mask: str | Omit = omit,
        back_channel_logout_uris: SequenceNotStr[str] | Omit = omit,
        default_redirect_uri: str | Omit = omit,
        initiate_login_uri: str | Omit = omit,
        post_login_uris: SequenceNotStr[str] | Omit = omit,
        post_logout_redirect_uris: SequenceNotStr[str] | Omit = omit,
        redirect_uris: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClientUpdateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not client_id:
            raise ValueError(f"Expected a non-empty value for `client_id` but received {client_id!r}")
        return await self._patch(
            f"/api/v1/clients/{client_id}",
            body=await async_maybe_transform(
                {
                    "back_channel_logout_uris": back_channel_logout_uris,
                    "default_redirect_uri": default_redirect_uri,
                    "initiate_login_uri": initiate_login_uri,
                    "post_login_uris": post_login_uris,
                    "post_logout_redirect_uris": post_logout_redirect_uris,
                    "redirect_uris": redirect_uris,
                },
                client_update_params.ClientUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"mask": mask}, client_update_params.ClientUpdateParams),
            ),
            cast_to=ClientUpdateResponse,
        )

    async def list(
        self,
        *,
        include_plain_secret: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClientListResponse:
        """
        Args:
          include_plain_secret: Controls whether plain secret values are included in the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/clients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include_plain_secret": include_plain_secret}, client_list_params.ClientListParams
                ),
            ),
            cast_to=ClientListResponse,
        )


class ClientsResourceWithRawResponse:
    def __init__(self, clients: ClientsResource) -> None:
        self._clients = clients

        self.retrieve = to_raw_response_wrapper(
            clients.retrieve,
        )
        self.update = to_raw_response_wrapper(
            clients.update,
        )
        self.list = to_raw_response_wrapper(
            clients.list,
        )

    @cached_property
    def secrets(self) -> SecretsResourceWithRawResponse:
        return SecretsResourceWithRawResponse(self._clients.secrets)


class AsyncClientsResourceWithRawResponse:
    def __init__(self, clients: AsyncClientsResource) -> None:
        self._clients = clients

        self.retrieve = async_to_raw_response_wrapper(
            clients.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            clients.update,
        )
        self.list = async_to_raw_response_wrapper(
            clients.list,
        )

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithRawResponse:
        return AsyncSecretsResourceWithRawResponse(self._clients.secrets)


class ClientsResourceWithStreamingResponse:
    def __init__(self, clients: ClientsResource) -> None:
        self._clients = clients

        self.retrieve = to_streamed_response_wrapper(
            clients.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            clients.update,
        )
        self.list = to_streamed_response_wrapper(
            clients.list,
        )

    @cached_property
    def secrets(self) -> SecretsResourceWithStreamingResponse:
        return SecretsResourceWithStreamingResponse(self._clients.secrets)


class AsyncClientsResourceWithStreamingResponse:
    def __init__(self, clients: AsyncClientsResource) -> None:
        self._clients = clients

        self.retrieve = async_to_streamed_response_wrapper(
            clients.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            clients.update,
        )
        self.list = async_to_streamed_response_wrapper(
            clients.list,
        )

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithStreamingResponse:
        return AsyncSecretsResourceWithStreamingResponse(self._clients.secrets)
