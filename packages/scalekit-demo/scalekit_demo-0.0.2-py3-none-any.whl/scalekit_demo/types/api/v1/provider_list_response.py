# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .provider import Provider
from ...._models import BaseModel

__all__ = ["ProviderListResponse"]


class ProviderListResponse(BaseModel):
    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    providers: Optional[List[Provider]] = None

    total_size: Optional[int] = None
