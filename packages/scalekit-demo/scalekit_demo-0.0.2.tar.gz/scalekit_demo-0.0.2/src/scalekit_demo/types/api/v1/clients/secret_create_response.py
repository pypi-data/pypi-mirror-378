# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from ..organizations.clients.client_secret import ClientSecret

__all__ = ["SecretCreateResponse"]


class SecretCreateResponse(BaseModel):
    plain_secret: Optional[str] = None
    """The unhashed secret value; only returned once at creation time"""

    secret: Optional[ClientSecret] = None
    """Metadata about the created secret (doesn't include the plain secret value)"""
