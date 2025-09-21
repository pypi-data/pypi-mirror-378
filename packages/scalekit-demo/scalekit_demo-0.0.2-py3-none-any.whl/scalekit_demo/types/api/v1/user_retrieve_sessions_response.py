# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .session_details import SessionDetails

__all__ = ["UserRetrieveSessionsResponse"]


class UserRetrieveSessionsResponse(BaseModel):
    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    sessions: Optional[List[SessionDetails]] = None

    total_size: Optional[int] = None
