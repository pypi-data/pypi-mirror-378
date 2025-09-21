# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ...._models import BaseModel
from .price_tier import PriceTier

__all__ = [
    "BillingRetrieveProductcatalogResponse",
    "Catalog",
    "CatalogProduct",
    "CatalogProductPrice",
    "CatalogProductProduct",
]


class CatalogProductPrice(BaseModel):
    id: Optional[str] = None

    amount: Optional[str] = None

    billing_scheme: Optional[str] = None

    currency: Optional[str] = None

    interval: Optional[str] = None

    tiers: Optional[List[PriceTier]] = None

    type: Optional[str] = None

    usage_type: Optional[str] = None


class CatalogProductProduct(BaseModel):
    id: Optional[str] = None

    active: Optional[bool] = None

    default_price_id: Optional[str] = None

    description: Optional[str] = None

    metadata: Optional[Dict[str, str]] = None

    name: Optional[str] = None


class CatalogProduct(BaseModel):
    billing_type: Optional[str] = None

    prices: Optional[List[CatalogProductPrice]] = None

    product: Optional[CatalogProductProduct] = None


class Catalog(BaseModel):
    products: Optional[List[CatalogProduct]] = None


class BillingRetrieveProductcatalogResponse(BaseModel):
    catalog: Optional[Catalog] = None
