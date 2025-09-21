# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .organizations.role import Role

__all__ = ["RoleListResponse"]


class RoleListResponse(BaseModel):
    roles: Optional[List[Role]] = None
