# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .user_attribute import UserAttribute

__all__ = ["ListUserAttributesResponse"]


class ListUserAttributesResponse(BaseModel):
    user_attributes: Optional[List[UserAttribute]] = None
