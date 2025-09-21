# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.api.v1 import scope_list_params, scope_create_params, scope_update_params
from ....types.api.v1.scope_update_response import ScopeUpdateResponse
from ....types.api.v1.environments.list_scopes_response import ListScopesResponse
from ....types.api.v1.environments.create_scope_response import CreateScopeResponse

__all__ = ["ScopesResource", "AsyncScopesResource"]


class ScopesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ScopesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return ScopesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScopesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return ScopesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        env_id: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CreateScopeResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/scopes",
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                },
                scope_create_params.ScopeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"env_id": env_id}, scope_create_params.ScopeCreateParams),
            ),
            cast_to=CreateScopeResponse,
        )

    def update(
        self,
        id: str,
        *,
        description: str | Omit = omit,
        enabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ScopeUpdateResponse:
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
            f"/api/v1/scopes/{id}",
            body=maybe_transform(
                {
                    "description": description,
                    "enabled": enabled,
                },
                scope_update_params.ScopeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScopeUpdateResponse,
        )

    def list(
        self,
        *,
        env_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListScopesResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/scopes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"env_id": env_id}, scope_list_params.ScopeListParams),
            ),
            cast_to=ListScopesResponse,
        )

    def delete(
        self,
        id: str,
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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/scopes/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncScopesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncScopesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncScopesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScopesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncScopesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        env_id: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CreateScopeResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/scopes",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                },
                scope_create_params.ScopeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"env_id": env_id}, scope_create_params.ScopeCreateParams),
            ),
            cast_to=CreateScopeResponse,
        )

    async def update(
        self,
        id: str,
        *,
        description: str | Omit = omit,
        enabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ScopeUpdateResponse:
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
            f"/api/v1/scopes/{id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "enabled": enabled,
                },
                scope_update_params.ScopeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScopeUpdateResponse,
        )

    async def list(
        self,
        *,
        env_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListScopesResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/scopes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"env_id": env_id}, scope_list_params.ScopeListParams),
            ),
            cast_to=ListScopesResponse,
        )

    async def delete(
        self,
        id: str,
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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/scopes/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ScopesResourceWithRawResponse:
    def __init__(self, scopes: ScopesResource) -> None:
        self._scopes = scopes

        self.create = to_raw_response_wrapper(
            scopes.create,
        )
        self.update = to_raw_response_wrapper(
            scopes.update,
        )
        self.list = to_raw_response_wrapper(
            scopes.list,
        )
        self.delete = to_raw_response_wrapper(
            scopes.delete,
        )


class AsyncScopesResourceWithRawResponse:
    def __init__(self, scopes: AsyncScopesResource) -> None:
        self._scopes = scopes

        self.create = async_to_raw_response_wrapper(
            scopes.create,
        )
        self.update = async_to_raw_response_wrapper(
            scopes.update,
        )
        self.list = async_to_raw_response_wrapper(
            scopes.list,
        )
        self.delete = async_to_raw_response_wrapper(
            scopes.delete,
        )


class ScopesResourceWithStreamingResponse:
    def __init__(self, scopes: ScopesResource) -> None:
        self._scopes = scopes

        self.create = to_streamed_response_wrapper(
            scopes.create,
        )
        self.update = to_streamed_response_wrapper(
            scopes.update,
        )
        self.list = to_streamed_response_wrapper(
            scopes.list,
        )
        self.delete = to_streamed_response_wrapper(
            scopes.delete,
        )


class AsyncScopesResourceWithStreamingResponse:
    def __init__(self, scopes: AsyncScopesResource) -> None:
        self._scopes = scopes

        self.create = async_to_streamed_response_wrapper(
            scopes.create,
        )
        self.update = async_to_streamed_response_wrapper(
            scopes.update,
        )
        self.list = async_to_streamed_response_wrapper(
            scopes.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            scopes.delete,
        )
