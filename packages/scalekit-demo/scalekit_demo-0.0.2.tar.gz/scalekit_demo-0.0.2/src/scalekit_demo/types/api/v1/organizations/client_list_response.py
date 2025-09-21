# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel
from .m2_m_client import M2MClient

__all__ = ["ClientListResponse"]


class ClientListResponse(BaseModel):
    clients: Optional[List[M2MClient]] = None
    """List of organization API clients"""

    next_page_token: Optional[str] = None
    """Pagination token for the next page of results"""

    prev_page_token: Optional[str] = None
    """Pagination token for the previous page of results"""

    total_size: Optional[int] = None
    """Total number of clients in the organization"""
