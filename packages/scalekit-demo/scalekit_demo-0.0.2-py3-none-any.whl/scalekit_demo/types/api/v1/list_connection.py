# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["ListConnection"]


class ListConnection(BaseModel):
    id: Optional[str] = None

    created_at: Optional[datetime] = None

    domains: Optional[List[str]] = None

    enabled: Optional[bool] = None

    key_id: Optional[str] = None

    organization_id: Optional[str] = None

    organization_name: Optional[str] = None

    provider: Optional[int] = None

    provider_key: Optional[str] = None

    status: Optional[int] = None

    type: Optional[int] = None

    ui_button_title: Optional[str] = None
