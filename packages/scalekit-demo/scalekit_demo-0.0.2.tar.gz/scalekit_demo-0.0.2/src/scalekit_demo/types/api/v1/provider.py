# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["Provider"]


class Provider(BaseModel):
    description: Optional[str] = None

    display_name: Optional[str] = None

    key_id: Optional[str] = None
