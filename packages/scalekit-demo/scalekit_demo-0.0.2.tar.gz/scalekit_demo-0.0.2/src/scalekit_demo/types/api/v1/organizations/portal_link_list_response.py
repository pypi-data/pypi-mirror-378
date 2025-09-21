# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .link import Link
from ....._models import BaseModel

__all__ = ["PortalLinkListResponse"]


class PortalLinkListResponse(BaseModel):
    links: Optional[List[Link]] = None
