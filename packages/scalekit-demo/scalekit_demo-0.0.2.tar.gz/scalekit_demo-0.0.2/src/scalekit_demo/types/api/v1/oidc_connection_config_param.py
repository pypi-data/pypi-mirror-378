# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

__all__ = ["OidcConnectionConfigParam"]


class OidcConnectionConfigParam(TypedDict, total=False):
    authorize_uri: str

    client_id: str

    client_secret: str

    discovery_endpoint: str

    idp_logout_required: bool

    issuer: str

    jwks_uri: str

    pkce_enabled: bool

    redirect_uri: str

    scopes: Iterable[int]

    token_auth_type: int

    token_uri: str

    user_info_uri: str
