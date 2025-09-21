# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["Scope"]


class Scope(BaseModel):
    id: Optional[str] = None

    description: Optional[str] = None

    enabled: Optional[bool] = None

    name: Optional[str] = None
