# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["OidcConnectionConfig"]


class OidcConnectionConfig(BaseModel):
    authorize_uri: Optional[str] = None

    backchannel_logout_redirect_uri: Optional[str] = None

    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    discovery_endpoint: Optional[str] = None

    idp_logout_required: Optional[bool] = None

    issuer: Optional[str] = None

    jwks_uri: Optional[str] = None

    pkce_enabled: Optional[bool] = None

    post_logout_redirect_uri: Optional[str] = None

    redirect_uri: Optional[str] = None

    scopes: Optional[List[int]] = None

    token_auth_type: Optional[int] = None

    token_uri: Optional[str] = None

    user_info_uri: Optional[str] = None
