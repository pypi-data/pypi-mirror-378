# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel
from .price_tier import PriceTier

__all__ = [
    "WorkspacesThisRetrieveBillingInfoResponse",
    "BillingInfo",
    "BillingInfoAddon",
    "BillingInfoBillingContactInfo",
    "BillingInfoCurrentInvoice",
    "BillingInfoLastInvoice",
    "BillingInfoPaymentMethod",
    "BillingInfoSubscription",
    "BillingInfoSubscriptionItem",
    "BillingInfoSubscriptionItemPrice",
    "BillingInfoSubscriptionItemProduct",
]


class BillingInfoAddon(BaseModel):
    id: Optional[str] = None

    currency: Optional[str] = None

    description: Optional[str] = None

    enabled: Optional[bool] = None

    features: Optional[List[str]] = None

    name: Optional[str] = None

    price: Optional[float] = None


class BillingInfoBillingContactInfo(BaseModel):
    city: Optional[str] = None

    country: Optional[str] = None

    email: Optional[str] = None

    line1: Optional[str] = None

    line2: Optional[str] = None

    name: Optional[str] = None

    postal_code: Optional[str] = None

    state: Optional[str] = None


class BillingInfoCurrentInvoice(BaseModel):
    id: Optional[str] = None

    amount: Optional[float] = None

    currency: Optional[str] = None

    due_date: Optional[datetime] = None

    issued_date: Optional[datetime] = None

    status: Optional[int] = None


class BillingInfoLastInvoice(BaseModel):
    id: Optional[str] = None

    amount: Optional[float] = None

    currency: Optional[str] = None

    due_date: Optional[datetime] = None

    issued_date: Optional[datetime] = None

    status: Optional[int] = None


class BillingInfoPaymentMethod(BaseModel):
    id: Optional[str] = None

    account_number: Optional[str] = None

    account_type: Optional[str] = None

    status: Optional[int] = None

    type: Optional[int] = None


class BillingInfoSubscriptionItemPrice(BaseModel):
    id: Optional[str] = None

    aggregation_method: Optional[str] = None

    amount: Optional[str] = None

    billing_scheme: Optional[str] = None

    interval: Optional[str] = None

    tiers: Optional[List[PriceTier]] = None

    total_usage: Optional[str] = None

    type: Optional[str] = None

    usage_type: Optional[str] = None


class BillingInfoSubscriptionItemProduct(BaseModel):
    id: Optional[str] = None

    active: Optional[bool] = None

    description: Optional[str] = None

    name: Optional[str] = None


class BillingInfoSubscriptionItem(BaseModel):
    id: Optional[str] = None

    price: Optional[BillingInfoSubscriptionItemPrice] = None

    price_id: Optional[str] = None

    product: Optional[BillingInfoSubscriptionItemProduct] = None

    quantity: Optional[str] = None


class BillingInfoSubscription(BaseModel):
    id: Optional[str] = None

    amount: Optional[float] = None

    currency: Optional[str] = None

    end_date: Optional[datetime] = None

    items: Optional[List[BillingInfoSubscriptionItem]] = None

    start_date: Optional[datetime] = None

    status: Optional[int] = None


class BillingInfo(BaseModel):
    addons: Optional[List[BillingInfoAddon]] = None

    billing_contact_info: Optional[BillingInfoBillingContactInfo] = None

    current_invoice: Optional[BillingInfoCurrentInvoice] = None

    last_invoice: Optional[BillingInfoLastInvoice] = None

    payment_method: Optional[BillingInfoPaymentMethod] = None

    plan_name: Optional[str] = None

    subscriptions: Optional[List[BillingInfoSubscription]] = None


class WorkspacesThisRetrieveBillingInfoResponse(BaseModel):
    billing_info: Optional[BillingInfo] = None
