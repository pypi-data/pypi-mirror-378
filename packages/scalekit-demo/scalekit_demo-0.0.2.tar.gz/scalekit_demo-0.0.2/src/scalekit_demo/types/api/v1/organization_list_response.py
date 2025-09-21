# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .organization import Organization

__all__ = ["OrganizationListResponse"]


class OrganizationListResponse(BaseModel):
    next_page_token: Optional[str] = None

    organizations: Optional[List[Organization]] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None
