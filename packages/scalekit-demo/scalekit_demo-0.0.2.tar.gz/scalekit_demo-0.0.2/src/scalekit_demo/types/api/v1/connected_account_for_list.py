# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["ConnectedAccountForList"]


class ConnectedAccountForList(BaseModel):
    id: Optional[str] = None

    authorization_type: Optional[int] = None

    connection_id: Optional[str] = None

    connector: Optional[str] = None

    identifier: Optional[str] = None

    last_used_at: Optional[datetime] = None

    provider: Optional[str] = None

    status: Optional[int] = None

    token_expires_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None
