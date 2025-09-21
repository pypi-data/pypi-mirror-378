# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .link import Link
from ....._models import BaseModel

__all__ = ["PortalLinkCreateResponse"]


class PortalLinkCreateResponse(BaseModel):
    link: Optional[Link] = None
