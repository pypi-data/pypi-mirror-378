# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["AuthorizationDetailsParam", "OAuthToken", "StaticAuth"]


class OAuthToken(TypedDict, total=False):
    access_token: str

    domain: str

    refresh_token: str

    scopes: SequenceNotStr[str]


class StaticAuth(TypedDict, total=False):
    details: object


class AuthorizationDetailsParam(TypedDict, total=False):
    oauth_token: OAuthToken

    static_auth: StaticAuth
