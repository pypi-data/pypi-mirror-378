# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ....._base_client import make_request_options
from .....types.api.v1.organizations import portal_link_create_params
from .....types.api.v1.organizations.portal_link_list_response import PortalLinkListResponse
from .....types.api.v1.organizations.portal_link_create_response import PortalLinkCreateResponse

__all__ = ["PortalLinksResource", "AsyncPortalLinksResource"]


class PortalLinksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PortalLinksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return PortalLinksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PortalLinksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return PortalLinksResourceWithStreamingResponse(self)

    def create(
        self,
        id: str,
        *,
        directory_sync: bool | Omit = omit,
        features: Iterable[int] | Omit = omit,
        sso: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PortalLinkCreateResponse:
        """
        Generate Portal Link for Org

        Args:
          directory_sync: Deprecated: Use features

          sso: Deprecated: Use features

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/api/v1/organizations/{id}/portal_links",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "directory_sync": directory_sync,
                        "features": features,
                        "sso": sso,
                    },
                    portal_link_create_params.PortalLinkCreateParams,
                ),
            ),
            cast_to=PortalLinkCreateResponse,
        )

    def list(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PortalLinkListResponse:
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
            f"/api/v1/organizations/{id}/portal_links",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PortalLinkListResponse,
        )

    def delete(
        self,
        link_id: str,
        *,
        id: str,
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
        if not link_id:
            raise ValueError(f"Expected a non-empty value for `link_id` but received {link_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/organizations/{id}/portal_links/{link_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def delete_all(
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
            f"/api/v1/organizations/{id}/portal_links",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncPortalLinksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPortalLinksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPortalLinksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPortalLinksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncPortalLinksResourceWithStreamingResponse(self)

    async def create(
        self,
        id: str,
        *,
        directory_sync: bool | Omit = omit,
        features: Iterable[int] | Omit = omit,
        sso: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PortalLinkCreateResponse:
        """
        Generate Portal Link for Org

        Args:
          directory_sync: Deprecated: Use features

          sso: Deprecated: Use features

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/api/v1/organizations/{id}/portal_links",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "directory_sync": directory_sync,
                        "features": features,
                        "sso": sso,
                    },
                    portal_link_create_params.PortalLinkCreateParams,
                ),
            ),
            cast_to=PortalLinkCreateResponse,
        )

    async def list(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PortalLinkListResponse:
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
            f"/api/v1/organizations/{id}/portal_links",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PortalLinkListResponse,
        )

    async def delete(
        self,
        link_id: str,
        *,
        id: str,
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
        if not link_id:
            raise ValueError(f"Expected a non-empty value for `link_id` but received {link_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/organizations/{id}/portal_links/{link_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete_all(
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
            f"/api/v1/organizations/{id}/portal_links",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class PortalLinksResourceWithRawResponse:
    def __init__(self, portal_links: PortalLinksResource) -> None:
        self._portal_links = portal_links

        self.create = to_raw_response_wrapper(
            portal_links.create,
        )
        self.list = to_raw_response_wrapper(
            portal_links.list,
        )
        self.delete = to_raw_response_wrapper(
            portal_links.delete,
        )
        self.delete_all = to_raw_response_wrapper(
            portal_links.delete_all,
        )


class AsyncPortalLinksResourceWithRawResponse:
    def __init__(self, portal_links: AsyncPortalLinksResource) -> None:
        self._portal_links = portal_links

        self.create = async_to_raw_response_wrapper(
            portal_links.create,
        )
        self.list = async_to_raw_response_wrapper(
            portal_links.list,
        )
        self.delete = async_to_raw_response_wrapper(
            portal_links.delete,
        )
        self.delete_all = async_to_raw_response_wrapper(
            portal_links.delete_all,
        )


class PortalLinksResourceWithStreamingResponse:
    def __init__(self, portal_links: PortalLinksResource) -> None:
        self._portal_links = portal_links

        self.create = to_streamed_response_wrapper(
            portal_links.create,
        )
        self.list = to_streamed_response_wrapper(
            portal_links.list,
        )
        self.delete = to_streamed_response_wrapper(
            portal_links.delete,
        )
        self.delete_all = to_streamed_response_wrapper(
            portal_links.delete_all,
        )


class AsyncPortalLinksResourceWithStreamingResponse:
    def __init__(self, portal_links: AsyncPortalLinksResource) -> None:
        self._portal_links = portal_links

        self.create = async_to_streamed_response_wrapper(
            portal_links.create,
        )
        self.list = async_to_streamed_response_wrapper(
            portal_links.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            portal_links.delete,
        )
        self.delete_all = async_to_streamed_response_wrapper(
            portal_links.delete_all,
        )
