# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ....types.api.v1 import workspaces_this_update_workspaces_this_params
from ....types.api.v1.get_workspace_response import GetWorkspaceResponse
from ....types.api.v1.update_workspace_response import UpdateWorkspaceResponse
from ....types.api.v1.workspaces_this_retrieve_billing_info_response import WorkspacesThisRetrieveBillingInfoResponse
from ....types.api.v1.workspaces_this_retrieve_billing_usage_response import WorkspacesThisRetrieveBillingUsageResponse

__all__ = ["WorkspacesThisResource", "AsyncWorkspacesThisResource"]


class WorkspacesThisResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WorkspacesThisResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return WorkspacesThisResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkspacesThisResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return WorkspacesThisResourceWithStreamingResponse(self)

    def retrieve_billing_info(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspacesThisRetrieveBillingInfoResponse:
        return self._get(
            "/api/v1/workspaces:this/billing:info",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspacesThisRetrieveBillingInfoResponse,
        )

    def retrieve_billing_usage(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspacesThisRetrieveBillingUsageResponse:
        return self._get(
            "/api/v1/workspaces:this/billing:usage",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspacesThisRetrieveBillingUsageResponse,
        )

    def retrieve_workspaces_this(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetWorkspaceResponse:
        return self._get(
            "/api/v1/workspaces:this",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetWorkspaceResponse,
        )

    def update_workspaces_this(
        self,
        *,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateWorkspaceResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            "/api/v1/workspaces:this",
            body=maybe_transform(
                {"display_name": display_name},
                workspaces_this_update_workspaces_this_params.WorkspacesThisUpdateWorkspacesThisParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateWorkspaceResponse,
        )


class AsyncWorkspacesThisResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWorkspacesThisResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkspacesThisResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkspacesThisResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncWorkspacesThisResourceWithStreamingResponse(self)

    async def retrieve_billing_info(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspacesThisRetrieveBillingInfoResponse:
        return await self._get(
            "/api/v1/workspaces:this/billing:info",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspacesThisRetrieveBillingInfoResponse,
        )

    async def retrieve_billing_usage(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspacesThisRetrieveBillingUsageResponse:
        return await self._get(
            "/api/v1/workspaces:this/billing:usage",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspacesThisRetrieveBillingUsageResponse,
        )

    async def retrieve_workspaces_this(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetWorkspaceResponse:
        return await self._get(
            "/api/v1/workspaces:this",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetWorkspaceResponse,
        )

    async def update_workspaces_this(
        self,
        *,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateWorkspaceResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            "/api/v1/workspaces:this",
            body=await async_maybe_transform(
                {"display_name": display_name},
                workspaces_this_update_workspaces_this_params.WorkspacesThisUpdateWorkspacesThisParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateWorkspaceResponse,
        )


class WorkspacesThisResourceWithRawResponse:
    def __init__(self, workspaces_this: WorkspacesThisResource) -> None:
        self._workspaces_this = workspaces_this

        self.retrieve_billing_info = to_raw_response_wrapper(
            workspaces_this.retrieve_billing_info,
        )
        self.retrieve_billing_usage = to_raw_response_wrapper(
            workspaces_this.retrieve_billing_usage,
        )
        self.retrieve_workspaces_this = to_raw_response_wrapper(
            workspaces_this.retrieve_workspaces_this,
        )
        self.update_workspaces_this = to_raw_response_wrapper(
            workspaces_this.update_workspaces_this,
        )


class AsyncWorkspacesThisResourceWithRawResponse:
    def __init__(self, workspaces_this: AsyncWorkspacesThisResource) -> None:
        self._workspaces_this = workspaces_this

        self.retrieve_billing_info = async_to_raw_response_wrapper(
            workspaces_this.retrieve_billing_info,
        )
        self.retrieve_billing_usage = async_to_raw_response_wrapper(
            workspaces_this.retrieve_billing_usage,
        )
        self.retrieve_workspaces_this = async_to_raw_response_wrapper(
            workspaces_this.retrieve_workspaces_this,
        )
        self.update_workspaces_this = async_to_raw_response_wrapper(
            workspaces_this.update_workspaces_this,
        )


class WorkspacesThisResourceWithStreamingResponse:
    def __init__(self, workspaces_this: WorkspacesThisResource) -> None:
        self._workspaces_this = workspaces_this

        self.retrieve_billing_info = to_streamed_response_wrapper(
            workspaces_this.retrieve_billing_info,
        )
        self.retrieve_billing_usage = to_streamed_response_wrapper(
            workspaces_this.retrieve_billing_usage,
        )
        self.retrieve_workspaces_this = to_streamed_response_wrapper(
            workspaces_this.retrieve_workspaces_this,
        )
        self.update_workspaces_this = to_streamed_response_wrapper(
            workspaces_this.update_workspaces_this,
        )


class AsyncWorkspacesThisResourceWithStreamingResponse:
    def __init__(self, workspaces_this: AsyncWorkspacesThisResource) -> None:
        self._workspaces_this = workspaces_this

        self.retrieve_billing_info = async_to_streamed_response_wrapper(
            workspaces_this.retrieve_billing_info,
        )
        self.retrieve_billing_usage = async_to_streamed_response_wrapper(
            workspaces_this.retrieve_billing_usage,
        )
        self.retrieve_workspaces_this = async_to_streamed_response_wrapper(
            workspaces_this.retrieve_workspaces_this,
        )
        self.update_workspaces_this = async_to_streamed_response_wrapper(
            workspaces_this.update_workspaces_this,
        )
