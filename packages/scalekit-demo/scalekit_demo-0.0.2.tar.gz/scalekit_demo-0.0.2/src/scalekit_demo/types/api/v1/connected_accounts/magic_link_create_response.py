# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["MagicLinkCreateResponse"]


class MagicLinkCreateResponse(BaseModel):
    expiry: Optional[datetime] = None

    link: Optional[str] = None
