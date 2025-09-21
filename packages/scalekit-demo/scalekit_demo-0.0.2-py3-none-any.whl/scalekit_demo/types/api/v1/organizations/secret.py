# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["Secret"]


class Secret(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    directory_id: Optional[str] = None

    expire_time: Optional[datetime] = None

    last_used_time: Optional[datetime] = None

    secret_suffix: Optional[str] = None

    status: Optional[int] = None
