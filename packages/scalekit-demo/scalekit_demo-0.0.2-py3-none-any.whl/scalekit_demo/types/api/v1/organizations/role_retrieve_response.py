# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .role import Role
from ....._models import BaseModel

__all__ = ["RoleRetrieveResponse"]


class RoleRetrieveResponse(BaseModel):
    role: Optional[Role] = None
