# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .fsa import (
    FsaResource,
    AsyncFsaResource,
    FsaResourceWithRawResponse,
    AsyncFsaResourceWithRawResponse,
    FsaResourceWithStreamingResponse,
    AsyncFsaResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["FeaturesResource", "AsyncFeaturesResource"]


class FeaturesResource(SyncAPIResource):
    @cached_property
    def fsa(self) -> FsaResource:
        return FsaResource(self._client)

    @cached_property
    def with_raw_response(self) -> FeaturesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return FeaturesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FeaturesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return FeaturesResourceWithStreamingResponse(self)


class AsyncFeaturesResource(AsyncAPIResource):
    @cached_property
    def fsa(self) -> AsyncFsaResource:
        return AsyncFsaResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFeaturesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFeaturesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFeaturesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/saif-at-scalekit/scalekit-demo-python#with_streaming_response
        """
        return AsyncFeaturesResourceWithStreamingResponse(self)


class FeaturesResourceWithRawResponse:
    def __init__(self, features: FeaturesResource) -> None:
        self._features = features

    @cached_property
    def fsa(self) -> FsaResourceWithRawResponse:
        return FsaResourceWithRawResponse(self._features.fsa)


class AsyncFeaturesResourceWithRawResponse:
    def __init__(self, features: AsyncFeaturesResource) -> None:
        self._features = features

    @cached_property
    def fsa(self) -> AsyncFsaResourceWithRawResponse:
        return AsyncFsaResourceWithRawResponse(self._features.fsa)


class FeaturesResourceWithStreamingResponse:
    def __init__(self, features: FeaturesResource) -> None:
        self._features = features

    @cached_property
    def fsa(self) -> FsaResourceWithStreamingResponse:
        return FsaResourceWithStreamingResponse(self._features.fsa)


class AsyncFeaturesResourceWithStreamingResponse:
    def __init__(self, features: AsyncFeaturesResource) -> None:
        self._features = features

    @cached_property
    def fsa(self) -> AsyncFsaResourceWithStreamingResponse:
        return AsyncFsaResourceWithStreamingResponse(self._features.fsa)
