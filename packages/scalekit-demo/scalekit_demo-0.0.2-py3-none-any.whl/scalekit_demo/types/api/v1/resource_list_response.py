# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .oauth.resource import Resource

__all__ = ["ResourceListResponse"]


class ResourceListResponse(BaseModel):
    next_page_token: Optional[str] = None

    resources: Optional[List[Resource]] = None

    total_size: Optional[int] = None
