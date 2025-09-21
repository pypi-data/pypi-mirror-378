# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["EventCreateResponse", "Event"]


class Event(BaseModel):
    id: Optional[str] = None

    data: Optional[object] = None

    display_name: Optional[str] = None

    environment_id: Optional[str] = None

    object: Optional[int] = None

    occurred_at: Optional[datetime] = None

    organization_id: Optional[str] = None

    spec_version: Optional[str] = None

    type: Optional[str] = None


class EventCreateResponse(BaseModel):
    events: Optional[List[Event]] = None

    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None
