# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["Role", "Permission"]


class Permission(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    description: Optional[str] = None

    name: Optional[str] = None

    role_name: Optional[str] = None

    update_time: Optional[datetime] = None


class Role(BaseModel):
    id: Optional[str] = None

    default_creator: Optional[bool] = None

    default_member: Optional[bool] = None

    dependent_roles_count: Optional[int] = None

    description: Optional[str] = None

    display_name: Optional[str] = None

    extends: Optional[str] = None

    is_org_role: Optional[bool] = None

    name: Optional[str] = None

    permissions: Optional[List[Permission]] = None
