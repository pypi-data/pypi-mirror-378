# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .client import Client
from ...._models import BaseModel

__all__ = ["ClientRetrieveResponse"]


class ClientRetrieveResponse(BaseModel):
    client: Optional[Client] = None
    """Complete client configuration with all settings"""
