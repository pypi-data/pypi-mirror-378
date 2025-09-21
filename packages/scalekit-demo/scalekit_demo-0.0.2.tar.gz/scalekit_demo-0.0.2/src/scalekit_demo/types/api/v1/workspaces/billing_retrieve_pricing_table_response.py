# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["BillingRetrievePricingTableResponse"]


class BillingRetrievePricingTableResponse(BaseModel):
    id: Optional[str] = None

    customer_session_client_secret: Optional[str] = None

    expiry: Optional[datetime] = None

    pricing_table_id: Optional[str] = None

    publishable_token: Optional[str] = None
