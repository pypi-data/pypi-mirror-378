# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["Permission"]


class Permission(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    description: Optional[str] = None

    name: Optional[str] = None

    update_time: Optional[datetime] = None
