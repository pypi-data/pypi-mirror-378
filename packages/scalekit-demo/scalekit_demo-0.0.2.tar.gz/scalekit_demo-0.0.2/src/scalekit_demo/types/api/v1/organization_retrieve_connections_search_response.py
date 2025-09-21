# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .list_connection import ListConnection

__all__ = ["OrganizationRetrieveConnectionsSearchResponse"]


class OrganizationRetrieveConnectionsSearchResponse(BaseModel):
    connections: Optional[List[ListConnection]] = None

    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None
