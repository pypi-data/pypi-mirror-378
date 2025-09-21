# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["OAuthConnectionConfig"]


class OAuthConnectionConfig(BaseModel):
    access_type: Optional[str] = None

    authorize_uri: Optional[str] = None

    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    custom_scope_name: Optional[str] = None

    pkce_enabled: Optional[bool] = None

    prompt: Optional[str] = None

    redirect_uri: Optional[str] = None

    scopes: Optional[List[str]] = None

    token_uri: Optional[str] = None

    use_platform_creds: Optional[bool] = None

    user_info_uri: Optional[str] = None
