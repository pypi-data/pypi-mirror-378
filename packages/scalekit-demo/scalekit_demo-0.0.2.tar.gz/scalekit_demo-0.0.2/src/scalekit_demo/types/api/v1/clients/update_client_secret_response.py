# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from ..organizations.clients.client_secret import ClientSecret

__all__ = ["UpdateClientSecretResponse"]


class UpdateClientSecretResponse(BaseModel):
    secret: Optional[ClientSecret] = None
    """Updated secret metadata"""
