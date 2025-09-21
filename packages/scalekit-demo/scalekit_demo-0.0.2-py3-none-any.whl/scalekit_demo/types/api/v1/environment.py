# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["Environment"]


class Environment(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    custom_domain: Optional[str] = None

    custom_domain_status: Optional[int] = None

    display_name: Optional[str] = None

    domain: Optional[str] = None

    region_code: Optional[int] = None

    type: Optional[int] = None

    update_time: Optional[datetime] = None
