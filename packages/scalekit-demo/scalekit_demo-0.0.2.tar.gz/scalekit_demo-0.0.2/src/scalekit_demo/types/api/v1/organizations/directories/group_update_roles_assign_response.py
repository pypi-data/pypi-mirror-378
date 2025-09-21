# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel
from .role_assignments import RoleAssignments

__all__ = ["GroupUpdateRolesAssignResponse"]


class GroupUpdateRolesAssignResponse(BaseModel):
    role_assignments: Optional[RoleAssignments] = None
