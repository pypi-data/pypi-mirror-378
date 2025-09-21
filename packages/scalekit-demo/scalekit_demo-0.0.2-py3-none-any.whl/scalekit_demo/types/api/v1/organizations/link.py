# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["Link"]


class Link(BaseModel):
    id: Optional[str] = None

    expire_time: Optional[datetime] = None

    location: Optional[str] = None
