# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .member import Member
from ...._models import BaseModel

__all__ = ["MemberListResponse"]


class MemberListResponse(BaseModel):
    members: Optional[List[Member]] = None

    next_page_token: Optional[str] = None

    total_size: Optional[int] = None
