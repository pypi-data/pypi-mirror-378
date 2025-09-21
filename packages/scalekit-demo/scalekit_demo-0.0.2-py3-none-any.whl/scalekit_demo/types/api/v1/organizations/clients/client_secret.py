# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ......_models import BaseModel

__all__ = ["ClientSecret"]


class ClientSecret(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    created_by: Optional[str] = None

    expire_time: Optional[datetime] = None

    last_used_time: Optional[datetime] = None

    plain_secret: Optional[str] = None

    secret_suffix: Optional[str] = None

    status: Optional[int] = None

    update_time: Optional[datetime] = None
