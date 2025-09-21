# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .environment import Environment

__all__ = ["EnvironmentListResponse"]


class EnvironmentListResponse(BaseModel):
    environments: Optional[List[Environment]] = None

    next_page_token: Optional[str] = None

    total_size: Optional[int] = None
