# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel

__all__ = ["BillingRetrieveSubscriptionsResponse", "Subscription"]


class Subscription(BaseModel):
    id: Optional[str] = None

    status: Optional[str] = None


class BillingRetrieveSubscriptionsResponse(BaseModel):
    id: Optional[str] = None

    subscriptions: Optional[List[Subscription]] = None
