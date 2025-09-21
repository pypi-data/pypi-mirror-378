# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["Location"]


class Location(BaseModel):
    city: Optional[str] = None

    latitude: Optional[str] = None

    longitude: Optional[str] = None

    region: Optional[str] = None

    region_subdivision: Optional[str] = None
