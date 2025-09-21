# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel

__all__ = ["AttributeMappings", "Attribute"]


class Attribute(BaseModel):
    key: Optional[str] = None

    map_to: Optional[str] = None


class AttributeMappings(BaseModel):
    attributes: Optional[List[Attribute]] = None
