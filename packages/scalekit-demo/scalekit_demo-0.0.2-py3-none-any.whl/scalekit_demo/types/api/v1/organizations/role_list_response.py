# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .role import Role
from ....._models import BaseModel

__all__ = ["RoleListResponse"]


class RoleListResponse(BaseModel):
    roles: Optional[List[Role]] = None
