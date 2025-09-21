# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["AuthorizationDetails", "OAuthToken", "StaticAuth"]


class OAuthToken(BaseModel):
    access_token: Optional[str] = None

    domain: Optional[str] = None

    refresh_token: Optional[str] = None

    scopes: Optional[List[str]] = None


class StaticAuth(BaseModel):
    details: Optional[object] = None


class AuthorizationDetails(BaseModel):
    oauth_token: Optional[OAuthToken] = None

    static_auth: Optional[StaticAuth] = None
