# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["Workspace", "ExtendedInfo"]


class ExtendedInfo(BaseModel):
    free_quota_exceeded: Optional[bool] = None

    payment_method_present: Optional[bool] = None

    payment_overdue: Optional[bool] = None


class Workspace(BaseModel):
    id: Optional[str] = None

    billing_customer_id: Optional[str] = None

    billing_subscription_id: Optional[str] = None

    create_time: Optional[datetime] = None

    display_name: Optional[str] = None

    extended_info: Optional[ExtendedInfo] = None

    region_code: Optional[int] = None

    update_time: Optional[datetime] = None
