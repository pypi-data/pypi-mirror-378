# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .client import Client
from ...._models import BaseModel

__all__ = ["ClientListResponse"]


class ClientListResponse(BaseModel):
    clients: Optional[List[Client]] = None
    """List of client resources"""

    total_size: Optional[int] = None
    """Total number of clients matching the query criteria"""
