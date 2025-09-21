# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["Tool"]


class Tool(BaseModel):
    id: Optional[str] = None

    definition: Optional[object] = None

    is_default: Optional[bool] = None

    metadata: Optional[object] = None

    provider: Optional[str] = None

    tags: Optional[List[str]] = None

    updated_at: Optional[datetime] = None
