# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .organizations.role import Role

__all__ = ["RoleCreateResponse"]


class RoleCreateResponse(BaseModel):
    role: Optional[Role] = None
