# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .domain import Domain
from ....._models import BaseModel

__all__ = ["DomainListResponse"]


class DomainListResponse(BaseModel):
    domains: Optional[List[Domain]] = None

    page_number: Optional[int] = None

    page_size: Optional[int] = None
