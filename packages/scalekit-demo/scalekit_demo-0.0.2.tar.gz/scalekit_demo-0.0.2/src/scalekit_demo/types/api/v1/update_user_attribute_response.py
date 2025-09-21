# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .user_attribute import UserAttribute

__all__ = ["UpdateUserAttributeResponse"]


class UpdateUserAttributeResponse(BaseModel):
    user_attribute: Optional[UserAttribute] = None
