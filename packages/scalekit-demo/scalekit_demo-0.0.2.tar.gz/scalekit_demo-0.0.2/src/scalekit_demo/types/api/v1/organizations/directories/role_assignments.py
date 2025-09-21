# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ......_models import BaseModel

__all__ = ["RoleAssignments", "Assignment"]


class Assignment(BaseModel):
    group_id: Optional[str] = None

    role_id: Optional[str] = None

    role_name: Optional[str] = None


class RoleAssignments(BaseModel):
    assignments: Optional[List[Assignment]] = None
