# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .permission import Permission

__all__ = ["PermissionCreateResponse"]


class PermissionCreateResponse(BaseModel):
    permission: Optional[Permission] = None
    """Permission Entity"""
