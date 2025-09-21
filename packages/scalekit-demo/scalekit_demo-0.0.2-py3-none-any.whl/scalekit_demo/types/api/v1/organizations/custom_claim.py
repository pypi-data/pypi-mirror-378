# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["CustomClaim"]


class CustomClaim(BaseModel):
    key: Optional[str] = None

    value: Optional[str] = None
