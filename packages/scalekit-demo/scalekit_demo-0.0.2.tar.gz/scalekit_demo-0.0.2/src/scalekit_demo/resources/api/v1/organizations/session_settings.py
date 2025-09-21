# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from .....types.api.v1.organizations import (
    session_setting_session_settings_params,
    session_setting_delete_session_settings_params,
    session_setting_update_session_settings_params,
    session_setting_retrieve_session_settings_params,
)
from .....types.api.v1.organizations.session_setting_session_settings_response import (
    SessionSettingSessionSettingsResponse,
)
from .....types.api.v1.organizations.session_setting_update_session_settings_response import (
    SessionSettingUpdateSessionSettingsResponse,
)
from .....types.api.v1.organizations.session_setting_retrieve_session_settings_response import (
    SessionSettingRetrieveSessionSettingsResponse,
)

__all__ = ["SessionSettingsResource", "AsyncSessionSettingsResource"]


class SessionSettingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SessionSettingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return SessionSettingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionSettingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return SessionSettingsResourceWithStreamingResponse(self)

    def delete_session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
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
            f"/api/v1/organizations/{id}/session-settings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_delete_session_settings_params.SessionSettingDeleteSessionSettingsParams,
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionSettingRetrieveSessionSettingsResponse:
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
            f"/api/v1/organizations/{id}/session-settings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_retrieve_session_settings_params.SessionSettingRetrieveSessionSettingsParams,
                ),
            ),
            cast_to=SessionSettingRetrieveSessionSettingsResponse,
        )

    def session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionSettingSessionSettingsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v1/organizations/{id}/session-settings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_session_settings_params.SessionSettingSessionSettingsParams,
                ),
            ),
            cast_to=SessionSettingSessionSettingsResponse,
        )

    def update_session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
        absolute_session_timeout: int | Omit = omit,
        idle_session_enabled: bool | Omit = omit,
        idle_session_timeout: int | Omit = omit,
        session_management_enabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionSettingUpdateSessionSettingsResponse:
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
            f"/api/v1/organizations/{id}/session-settings",
            body=maybe_transform(
                {
                    "absolute_session_timeout": absolute_session_timeout,
                    "idle_session_enabled": idle_session_enabled,
                    "idle_session_timeout": idle_session_timeout,
                    "session_management_enabled": session_management_enabled,
                },
                session_setting_update_session_settings_params.SessionSettingUpdateSessionSettingsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_update_session_settings_params.SessionSettingUpdateSessionSettingsParams,
                ),
            ),
            cast_to=SessionSettingUpdateSessionSettingsResponse,
        )


class AsyncSessionSettingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSessionSettingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionSettingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionSettingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncSessionSettingsResourceWithStreamingResponse(self)

    async def delete_session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
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
            f"/api/v1/organizations/{id}/session-settings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_delete_session_settings_params.SessionSettingDeleteSessionSettingsParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionSettingRetrieveSessionSettingsResponse:
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
            f"/api/v1/organizations/{id}/session-settings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_retrieve_session_settings_params.SessionSettingRetrieveSessionSettingsParams,
                ),
            ),
            cast_to=SessionSettingRetrieveSessionSettingsResponse,
        )

    async def session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionSettingSessionSettingsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v1/organizations/{id}/session-settings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_session_settings_params.SessionSettingSessionSettingsParams,
                ),
            ),
            cast_to=SessionSettingSessionSettingsResponse,
        )

    async def update_session_settings(
        self,
        id: str,
        *,
        environment_id: str | Omit = omit,
        absolute_session_timeout: int | Omit = omit,
        idle_session_enabled: bool | Omit = omit,
        idle_session_timeout: int | Omit = omit,
        session_management_enabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionSettingUpdateSessionSettingsResponse:
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
            f"/api/v1/organizations/{id}/session-settings",
            body=await async_maybe_transform(
                {
                    "absolute_session_timeout": absolute_session_timeout,
                    "idle_session_enabled": idle_session_enabled,
                    "idle_session_timeout": idle_session_timeout,
                    "session_management_enabled": session_management_enabled,
                },
                session_setting_update_session_settings_params.SessionSettingUpdateSessionSettingsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"environment_id": environment_id},
                    session_setting_update_session_settings_params.SessionSettingUpdateSessionSettingsParams,
                ),
            ),
            cast_to=SessionSettingUpdateSessionSettingsResponse,
        )


class SessionSettingsResourceWithRawResponse:
    def __init__(self, session_settings: SessionSettingsResource) -> None:
        self._session_settings = session_settings

        self.delete_session_settings = to_raw_response_wrapper(
            session_settings.delete_session_settings,
        )
        self.retrieve_session_settings = to_raw_response_wrapper(
            session_settings.retrieve_session_settings,
        )
        self.session_settings = to_raw_response_wrapper(
            session_settings.session_settings,
        )
        self.update_session_settings = to_raw_response_wrapper(
            session_settings.update_session_settings,
        )


class AsyncSessionSettingsResourceWithRawResponse:
    def __init__(self, session_settings: AsyncSessionSettingsResource) -> None:
        self._session_settings = session_settings

        self.delete_session_settings = async_to_raw_response_wrapper(
            session_settings.delete_session_settings,
        )
        self.retrieve_session_settings = async_to_raw_response_wrapper(
            session_settings.retrieve_session_settings,
        )
        self.session_settings = async_to_raw_response_wrapper(
            session_settings.session_settings,
        )
        self.update_session_settings = async_to_raw_response_wrapper(
            session_settings.update_session_settings,
        )


class SessionSettingsResourceWithStreamingResponse:
    def __init__(self, session_settings: SessionSettingsResource) -> None:
        self._session_settings = session_settings

        self.delete_session_settings = to_streamed_response_wrapper(
            session_settings.delete_session_settings,
        )
        self.retrieve_session_settings = to_streamed_response_wrapper(
            session_settings.retrieve_session_settings,
        )
        self.session_settings = to_streamed_response_wrapper(
            session_settings.session_settings,
        )
        self.update_session_settings = to_streamed_response_wrapper(
            session_settings.update_session_settings,
        )


class AsyncSessionSettingsResourceWithStreamingResponse:
    def __init__(self, session_settings: AsyncSessionSettingsResource) -> None:
        self._session_settings = session_settings

        self.delete_session_settings = async_to_streamed_response_wrapper(
            session_settings.delete_session_settings,
        )
        self.retrieve_session_settings = async_to_streamed_response_wrapper(
            session_settings.retrieve_session_settings,
        )
        self.session_settings = async_to_streamed_response_wrapper(
            session_settings.session_settings,
        )
        self.update_session_settings = async_to_streamed_response_wrapper(
            session_settings.update_session_settings,
        )
