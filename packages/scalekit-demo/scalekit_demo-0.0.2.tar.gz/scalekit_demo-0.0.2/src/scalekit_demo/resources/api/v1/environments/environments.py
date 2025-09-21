# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .scopes import (
    ScopesResource,
    AsyncScopesResource,
    ScopesResourceWithRawResponse,
    AsyncScopesResourceWithRawResponse,
    ScopesResourceWithStreamingResponse,
    AsyncScopesResourceWithStreamingResponse,
)
from .contexts import (
    ContextsResource,
    AsyncContextsResource,
    ContextsResourceWithRawResponse,
    AsyncContextsResourceWithRawResponse,
    ContextsResourceWithStreamingResponse,
    AsyncContextsResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .sessions_me import (
    SessionsMeResource,
    AsyncSessionsMeResource,
    SessionsMeResourceWithRawResponse,
    AsyncSessionsMeResourceWithRawResponse,
    SessionsMeResourceWithStreamingResponse,
    AsyncSessionsMeResourceWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1 import (
    environment_dns_params,
    environment_list_params,
    environment_asset_params,
    environment_create_params,
    environment_update_params,
    environment_dns_verify_params,
    environment_custom_domains_params,
    environment_update_id_update_params,
    environment_custom_domains_check_params,
    environment_update_customizations_params,
    environment_saml_certificates_generate_params,
)
from .session_settings import (
    SessionSettingsResource,
    AsyncSessionSettingsResource,
    SessionSettingsResourceWithRawResponse,
    AsyncSessionSettingsResourceWithRawResponse,
    SessionSettingsResourceWithStreamingResponse,
    AsyncSessionSettingsResourceWithStreamingResponse,
)
from .features.features import (
    FeaturesResource,
    AsyncFeaturesResource,
    FeaturesResourceWithRawResponse,
    AsyncFeaturesResourceWithRawResponse,
    FeaturesResourceWithStreamingResponse,
    AsyncFeaturesResourceWithStreamingResponse,
)
from .settings.settings import (
    SettingsResource,
    AsyncSettingsResource,
    SettingsResourceWithRawResponse,
    AsyncSettingsResourceWithRawResponse,
    SettingsResourceWithStreamingResponse,
    AsyncSettingsResourceWithStreamingResponse,
)
from .portal_customizations import (
    PortalCustomizationsResource,
    AsyncPortalCustomizationsResource,
    PortalCustomizationsResourceWithRawResponse,
    AsyncPortalCustomizationsResourceWithRawResponse,
    PortalCustomizationsResourceWithStreamingResponse,
    AsyncPortalCustomizationsResourceWithStreamingResponse,
)
from .....types.api.v1.environment_dns_response import EnvironmentDNSResponse
from .....types.api.v1.get_environment_response import GetEnvironmentResponse
from .....types.api.v1.environment_list_response import EnvironmentListResponse
from .....types.api.v1.environment_asset_response import EnvironmentAssetResponse
from .....types.api.v1.environment_create_response import EnvironmentCreateResponse
from .....types.api.v1.update_environment_response import UpdateEnvironmentResponse
from .....types.api.v1.environment_custom_domains_response import EnvironmentCustomDomainsResponse
from .....types.api.v1.update_portal_customization_response import UpdatePortalCustomizationResponse
from .....types.api.v1.environment_saml_certificates_generate_response import (
    EnvironmentSAMLCertificatesGenerateResponse,
)

__all__ = ["EnvironmentsResource", "AsyncEnvironmentsResource"]


class EnvironmentsResource(SyncAPIResource):
    @cached_property
    def portal_customizations(self) -> PortalCustomizationsResource:
        return PortalCustomizationsResource(self._client)

    @cached_property
    def sessions_me(self) -> SessionsMeResource:
        return SessionsMeResource(self._client)

    @cached_property
    def scopes(self) -> ScopesResource:
        return ScopesResource(self._client)

    @cached_property
    def contexts(self) -> ContextsResource:
        return ContextsResource(self._client)

    @cached_property
    def features(self) -> FeaturesResource:
        return FeaturesResource(self._client)

    @cached_property
    def session_settings(self) -> SessionSettingsResource:
        return SessionSettingsResource(self._client)

    @cached_property
    def settings(self) -> SettingsResource:
        return SettingsResource(self._client)

    @cached_property
    def with_raw_response(self) -> EnvironmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return EnvironmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EnvironmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return EnvironmentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        display_name: str | Omit = omit,
        region_code: int | Omit = omit,
        type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/environments",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "region_code": region_code,
                    "type": type,
                },
                environment_create_params.EnvironmentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetEnvironmentResponse:
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
            f"/api/v1/environments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetEnvironmentResponse,
        )

    def update(
        self,
        id: str,
        *,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateEnvironmentResponse:
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
            f"/api/v1/environments/{id}",
            body=maybe_transform({"display_name": display_name}, environment_update_params.EnvironmentUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateEnvironmentResponse,
        )

    def list(
        self,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/environments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    environment_list_params.EnvironmentListParams,
                ),
            ),
            cast_to=EnvironmentListResponse,
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
            f"/api/v1/environments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def asset(
        self,
        id: str,
        *,
        category: int | Omit = omit,
        extension: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentAssetResponse:
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
            f"/api/v1/environments/{id}/asset",
            body=maybe_transform(
                {
                    "category": category,
                    "extension": extension,
                },
                environment_asset_params.EnvironmentAssetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentAssetResponse,
        )

    def custom_domains(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        custom_domain: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentCustomDomainsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/api/v1/environments/{path_id}/custom-domains",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "custom_domain": custom_domain,
                },
                environment_custom_domains_params.EnvironmentCustomDomainsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentCustomDomainsResponse,
        )

    def custom_domains_check(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetEnvironmentResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/api/v1/environments/{path_id}/custom-domains:check",
            body=maybe_transform(
                {"body_id": body_id}, environment_custom_domains_check_params.EnvironmentCustomDomainsCheckParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetEnvironmentResponse,
        )

    def dns(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        custom_domain: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentDNSResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/api/v1/environments/{path_id}/dns",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "custom_domain": custom_domain,
                },
                environment_dns_params.EnvironmentDNSParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentDNSResponse,
        )

    def dns_verify(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        custom_domain: str | Omit = omit,
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
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/environments/{path_id}/dns:verify",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "custom_domain": custom_domain,
                },
                environment_dns_verify_params.EnvironmentDNSVerifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def saml_certificates_generate(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentSAMLCertificatesGenerateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/api/v1/environments/{path_id}/saml-certificates:generate",
            body=maybe_transform(
                {"body_id": body_id},
                environment_saml_certificates_generate_params.EnvironmentSAMLCertificatesGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentSAMLCertificatesGenerateResponse,
        )

    def update_customizations(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdatePortalCustomizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/api/v1/environments/{id}/customizations",
            body=maybe_transform(body, environment_update_customizations_params.EnvironmentUpdateCustomizationsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdatePortalCustomizationResponse,
        )

    def update_id_update(
        self,
        id: str,
        *,
        domain: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateEnvironmentResponse:
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
            f"/api/v1/environments/{id}:update",
            body=maybe_transform(
                {"domain": domain}, environment_update_id_update_params.EnvironmentUpdateIDUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateEnvironmentResponse,
        )


class AsyncEnvironmentsResource(AsyncAPIResource):
    @cached_property
    def portal_customizations(self) -> AsyncPortalCustomizationsResource:
        return AsyncPortalCustomizationsResource(self._client)

    @cached_property
    def sessions_me(self) -> AsyncSessionsMeResource:
        return AsyncSessionsMeResource(self._client)

    @cached_property
    def scopes(self) -> AsyncScopesResource:
        return AsyncScopesResource(self._client)

    @cached_property
    def contexts(self) -> AsyncContextsResource:
        return AsyncContextsResource(self._client)

    @cached_property
    def features(self) -> AsyncFeaturesResource:
        return AsyncFeaturesResource(self._client)

    @cached_property
    def session_settings(self) -> AsyncSessionSettingsResource:
        return AsyncSessionSettingsResource(self._client)

    @cached_property
    def settings(self) -> AsyncSettingsResource:
        return AsyncSettingsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEnvironmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEnvironmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEnvironmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncEnvironmentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        display_name: str | Omit = omit,
        region_code: int | Omit = omit,
        type: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/environments",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "region_code": region_code,
                    "type": type,
                },
                environment_create_params.EnvironmentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetEnvironmentResponse:
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
            f"/api/v1/environments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetEnvironmentResponse,
        )

    async def update(
        self,
        id: str,
        *,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateEnvironmentResponse:
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
            f"/api/v1/environments/{id}",
            body=await async_maybe_transform(
                {"display_name": display_name}, environment_update_params.EnvironmentUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateEnvironmentResponse,
        )

    async def list(
        self,
        *,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/environments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    environment_list_params.EnvironmentListParams,
                ),
            ),
            cast_to=EnvironmentListResponse,
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
            f"/api/v1/environments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def asset(
        self,
        id: str,
        *,
        category: int | Omit = omit,
        extension: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentAssetResponse:
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
            f"/api/v1/environments/{id}/asset",
            body=await async_maybe_transform(
                {
                    "category": category,
                    "extension": extension,
                },
                environment_asset_params.EnvironmentAssetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentAssetResponse,
        )

    async def custom_domains(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        custom_domain: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentCustomDomainsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/api/v1/environments/{path_id}/custom-domains",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "custom_domain": custom_domain,
                },
                environment_custom_domains_params.EnvironmentCustomDomainsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentCustomDomainsResponse,
        )

    async def custom_domains_check(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetEnvironmentResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/api/v1/environments/{path_id}/custom-domains:check",
            body=await async_maybe_transform(
                {"body_id": body_id}, environment_custom_domains_check_params.EnvironmentCustomDomainsCheckParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetEnvironmentResponse,
        )

    async def dns(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        custom_domain: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentDNSResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/api/v1/environments/{path_id}/dns",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "custom_domain": custom_domain,
                },
                environment_dns_params.EnvironmentDNSParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentDNSResponse,
        )

    async def dns_verify(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        custom_domain: str | Omit = omit,
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
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/environments/{path_id}/dns:verify",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "custom_domain": custom_domain,
                },
                environment_dns_verify_params.EnvironmentDNSVerifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def saml_certificates_generate(
        self,
        path_id: str,
        *,
        body_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentSAMLCertificatesGenerateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/api/v1/environments/{path_id}/saml-certificates:generate",
            body=await async_maybe_transform(
                {"body_id": body_id},
                environment_saml_certificates_generate_params.EnvironmentSAMLCertificatesGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnvironmentSAMLCertificatesGenerateResponse,
        )

    async def update_customizations(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdatePortalCustomizationResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/api/v1/environments/{id}/customizations",
            body=await async_maybe_transform(
                body, environment_update_customizations_params.EnvironmentUpdateCustomizationsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdatePortalCustomizationResponse,
        )

    async def update_id_update(
        self,
        id: str,
        *,
        domain: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UpdateEnvironmentResponse:
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
            f"/api/v1/environments/{id}:update",
            body=await async_maybe_transform(
                {"domain": domain}, environment_update_id_update_params.EnvironmentUpdateIDUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateEnvironmentResponse,
        )


class EnvironmentsResourceWithRawResponse:
    def __init__(self, environments: EnvironmentsResource) -> None:
        self._environments = environments

        self.create = to_raw_response_wrapper(
            environments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            environments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            environments.update,
        )
        self.list = to_raw_response_wrapper(
            environments.list,
        )
        self.delete = to_raw_response_wrapper(
            environments.delete,
        )
        self.asset = to_raw_response_wrapper(
            environments.asset,
        )
        self.custom_domains = to_raw_response_wrapper(
            environments.custom_domains,
        )
        self.custom_domains_check = to_raw_response_wrapper(
            environments.custom_domains_check,
        )
        self.dns = to_raw_response_wrapper(
            environments.dns,
        )
        self.dns_verify = to_raw_response_wrapper(
            environments.dns_verify,
        )
        self.saml_certificates_generate = to_raw_response_wrapper(
            environments.saml_certificates_generate,
        )
        self.update_customizations = to_raw_response_wrapper(
            environments.update_customizations,
        )
        self.update_id_update = to_raw_response_wrapper(
            environments.update_id_update,
        )

    @cached_property
    def portal_customizations(self) -> PortalCustomizationsResourceWithRawResponse:
        return PortalCustomizationsResourceWithRawResponse(self._environments.portal_customizations)

    @cached_property
    def sessions_me(self) -> SessionsMeResourceWithRawResponse:
        return SessionsMeResourceWithRawResponse(self._environments.sessions_me)

    @cached_property
    def scopes(self) -> ScopesResourceWithRawResponse:
        return ScopesResourceWithRawResponse(self._environments.scopes)

    @cached_property
    def contexts(self) -> ContextsResourceWithRawResponse:
        return ContextsResourceWithRawResponse(self._environments.contexts)

    @cached_property
    def features(self) -> FeaturesResourceWithRawResponse:
        return FeaturesResourceWithRawResponse(self._environments.features)

    @cached_property
    def session_settings(self) -> SessionSettingsResourceWithRawResponse:
        return SessionSettingsResourceWithRawResponse(self._environments.session_settings)

    @cached_property
    def settings(self) -> SettingsResourceWithRawResponse:
        return SettingsResourceWithRawResponse(self._environments.settings)


class AsyncEnvironmentsResourceWithRawResponse:
    def __init__(self, environments: AsyncEnvironmentsResource) -> None:
        self._environments = environments

        self.create = async_to_raw_response_wrapper(
            environments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            environments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            environments.update,
        )
        self.list = async_to_raw_response_wrapper(
            environments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            environments.delete,
        )
        self.asset = async_to_raw_response_wrapper(
            environments.asset,
        )
        self.custom_domains = async_to_raw_response_wrapper(
            environments.custom_domains,
        )
        self.custom_domains_check = async_to_raw_response_wrapper(
            environments.custom_domains_check,
        )
        self.dns = async_to_raw_response_wrapper(
            environments.dns,
        )
        self.dns_verify = async_to_raw_response_wrapper(
            environments.dns_verify,
        )
        self.saml_certificates_generate = async_to_raw_response_wrapper(
            environments.saml_certificates_generate,
        )
        self.update_customizations = async_to_raw_response_wrapper(
            environments.update_customizations,
        )
        self.update_id_update = async_to_raw_response_wrapper(
            environments.update_id_update,
        )

    @cached_property
    def portal_customizations(self) -> AsyncPortalCustomizationsResourceWithRawResponse:
        return AsyncPortalCustomizationsResourceWithRawResponse(self._environments.portal_customizations)

    @cached_property
    def sessions_me(self) -> AsyncSessionsMeResourceWithRawResponse:
        return AsyncSessionsMeResourceWithRawResponse(self._environments.sessions_me)

    @cached_property
    def scopes(self) -> AsyncScopesResourceWithRawResponse:
        return AsyncScopesResourceWithRawResponse(self._environments.scopes)

    @cached_property
    def contexts(self) -> AsyncContextsResourceWithRawResponse:
        return AsyncContextsResourceWithRawResponse(self._environments.contexts)

    @cached_property
    def features(self) -> AsyncFeaturesResourceWithRawResponse:
        return AsyncFeaturesResourceWithRawResponse(self._environments.features)

    @cached_property
    def session_settings(self) -> AsyncSessionSettingsResourceWithRawResponse:
        return AsyncSessionSettingsResourceWithRawResponse(self._environments.session_settings)

    @cached_property
    def settings(self) -> AsyncSettingsResourceWithRawResponse:
        return AsyncSettingsResourceWithRawResponse(self._environments.settings)


class EnvironmentsResourceWithStreamingResponse:
    def __init__(self, environments: EnvironmentsResource) -> None:
        self._environments = environments

        self.create = to_streamed_response_wrapper(
            environments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            environments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            environments.update,
        )
        self.list = to_streamed_response_wrapper(
            environments.list,
        )
        self.delete = to_streamed_response_wrapper(
            environments.delete,
        )
        self.asset = to_streamed_response_wrapper(
            environments.asset,
        )
        self.custom_domains = to_streamed_response_wrapper(
            environments.custom_domains,
        )
        self.custom_domains_check = to_streamed_response_wrapper(
            environments.custom_domains_check,
        )
        self.dns = to_streamed_response_wrapper(
            environments.dns,
        )
        self.dns_verify = to_streamed_response_wrapper(
            environments.dns_verify,
        )
        self.saml_certificates_generate = to_streamed_response_wrapper(
            environments.saml_certificates_generate,
        )
        self.update_customizations = to_streamed_response_wrapper(
            environments.update_customizations,
        )
        self.update_id_update = to_streamed_response_wrapper(
            environments.update_id_update,
        )

    @cached_property
    def portal_customizations(self) -> PortalCustomizationsResourceWithStreamingResponse:
        return PortalCustomizationsResourceWithStreamingResponse(self._environments.portal_customizations)

    @cached_property
    def sessions_me(self) -> SessionsMeResourceWithStreamingResponse:
        return SessionsMeResourceWithStreamingResponse(self._environments.sessions_me)

    @cached_property
    def scopes(self) -> ScopesResourceWithStreamingResponse:
        return ScopesResourceWithStreamingResponse(self._environments.scopes)

    @cached_property
    def contexts(self) -> ContextsResourceWithStreamingResponse:
        return ContextsResourceWithStreamingResponse(self._environments.contexts)

    @cached_property
    def features(self) -> FeaturesResourceWithStreamingResponse:
        return FeaturesResourceWithStreamingResponse(self._environments.features)

    @cached_property
    def session_settings(self) -> SessionSettingsResourceWithStreamingResponse:
        return SessionSettingsResourceWithStreamingResponse(self._environments.session_settings)

    @cached_property
    def settings(self) -> SettingsResourceWithStreamingResponse:
        return SettingsResourceWithStreamingResponse(self._environments.settings)


class AsyncEnvironmentsResourceWithStreamingResponse:
    def __init__(self, environments: AsyncEnvironmentsResource) -> None:
        self._environments = environments

        self.create = async_to_streamed_response_wrapper(
            environments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            environments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            environments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            environments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            environments.delete,
        )
        self.asset = async_to_streamed_response_wrapper(
            environments.asset,
        )
        self.custom_domains = async_to_streamed_response_wrapper(
            environments.custom_domains,
        )
        self.custom_domains_check = async_to_streamed_response_wrapper(
            environments.custom_domains_check,
        )
        self.dns = async_to_streamed_response_wrapper(
            environments.dns,
        )
        self.dns_verify = async_to_streamed_response_wrapper(
            environments.dns_verify,
        )
        self.saml_certificates_generate = async_to_streamed_response_wrapper(
            environments.saml_certificates_generate,
        )
        self.update_customizations = async_to_streamed_response_wrapper(
            environments.update_customizations,
        )
        self.update_id_update = async_to_streamed_response_wrapper(
            environments.update_id_update,
        )

    @cached_property
    def portal_customizations(self) -> AsyncPortalCustomizationsResourceWithStreamingResponse:
        return AsyncPortalCustomizationsResourceWithStreamingResponse(self._environments.portal_customizations)

    @cached_property
    def sessions_me(self) -> AsyncSessionsMeResourceWithStreamingResponse:
        return AsyncSessionsMeResourceWithStreamingResponse(self._environments.sessions_me)

    @cached_property
    def scopes(self) -> AsyncScopesResourceWithStreamingResponse:
        return AsyncScopesResourceWithStreamingResponse(self._environments.scopes)

    @cached_property
    def contexts(self) -> AsyncContextsResourceWithStreamingResponse:
        return AsyncContextsResourceWithStreamingResponse(self._environments.contexts)

    @cached_property
    def features(self) -> AsyncFeaturesResourceWithStreamingResponse:
        return AsyncFeaturesResourceWithStreamingResponse(self._environments.features)

    @cached_property
    def session_settings(self) -> AsyncSessionSettingsResourceWithStreamingResponse:
        return AsyncSessionSettingsResourceWithStreamingResponse(self._environments.session_settings)

    @cached_property
    def settings(self) -> AsyncSettingsResourceWithStreamingResponse:
        return AsyncSettingsResourceWithStreamingResponse(self._environments.settings)
