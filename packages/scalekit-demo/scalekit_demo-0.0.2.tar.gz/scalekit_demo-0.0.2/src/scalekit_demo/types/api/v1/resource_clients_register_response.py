# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel
from .organizations.custom_claim import CustomClaim
from .organizations.clients.client_secret import ClientSecret

__all__ = ["ResourceClientsRegisterResponse"]


class ResourceClientsRegisterResponse(BaseModel):
    audience: Optional[List[str]] = None

    client_id: Optional[str] = None

    create_time: Optional[datetime] = None

    custom_claims: Optional[List[CustomClaim]] = None

    description: Optional[str] = None

    expiry: Optional[str] = None

    name: Optional[str] = None

    redirect_uris: Optional[List[str]] = None

    resource_id: Optional[str] = None

    scopes: Optional[List[str]] = None

    secrets: Optional[List[ClientSecret]] = None

    update_time: Optional[datetime] = None
