# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["WorkspacesThisRetrieveBillingUsageResponse", "Product", "ProductTier"]


class ProductTier(BaseModel):
    currency: Optional[str] = None

    current_count: Optional[str] = None

    is_free_tier: Optional[bool] = None

    price_for_current_tier: Optional[float] = None

    tier_name: Optional[str] = None

    total_available_count: Optional[str] = None


class Product(BaseModel):
    currency: Optional[str] = None

    description: Optional[str] = None

    product_id: Optional[str] = None

    product_name: Optional[str] = None

    tiers: Optional[List[ProductTier]] = None

    total_product_amount: Optional[float] = None


class WorkspacesThisRetrieveBillingUsageResponse(BaseModel):
    currency: Optional[str] = None

    products: Optional[List[Product]] = None

    total_amount: Optional[float] = None
