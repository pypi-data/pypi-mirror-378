# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["PriceTier"]


class PriceTier(BaseModel):
    amount: Optional[str] = None

    up_to: Optional[str] = None
