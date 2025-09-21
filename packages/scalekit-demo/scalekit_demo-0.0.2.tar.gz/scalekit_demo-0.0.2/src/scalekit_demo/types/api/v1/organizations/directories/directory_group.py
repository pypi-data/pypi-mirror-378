# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ......_models import BaseModel

__all__ = ["DirectoryGroup"]


class DirectoryGroup(BaseModel):
    id: Optional[str] = None

    display_name: Optional[str] = None

    group_detail: Optional[object] = None

    total_users: Optional[int] = None

    updated_at: Optional[datetime] = None
