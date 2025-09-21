# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .v1.connections.user import User

__all__ = ["V1RetrieveUsersSearchResponse"]


class V1RetrieveUsersSearchResponse(BaseModel):
    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None

    users: Optional[List[User]] = None
