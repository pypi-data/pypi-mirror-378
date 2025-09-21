# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .list_connection import ListConnection

__all__ = ["ConnectionListResponse"]


class ConnectionListResponse(BaseModel):
    connections: Optional[List[ListConnection]] = None
