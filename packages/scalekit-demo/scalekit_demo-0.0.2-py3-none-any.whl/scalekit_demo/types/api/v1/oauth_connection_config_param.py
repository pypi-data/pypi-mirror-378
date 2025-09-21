# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["OAuthConnectionConfigParam"]


class OAuthConnectionConfigParam(TypedDict, total=False):
    access_type: str

    authorize_uri: str

    client_id: str

    client_secret: str

    custom_scope_name: str

    pkce_enabled: bool

    prompt: str

    redirect_uri: str

    scopes: SequenceNotStr[str]

    token_uri: str

    use_platform_creds: bool

    user_info_uri: str
