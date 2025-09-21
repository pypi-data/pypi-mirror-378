# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .secret import Secret
from ....._models import BaseModel
from .attribute_mappings import AttributeMappings
from .directories.role_assignments import RoleAssignments

__all__ = ["Directory", "Stats"]


class Stats(BaseModel):
    group_updated_at: Optional[datetime] = None

    total_groups: Optional[int] = None

    total_users: Optional[int] = None

    user_updated_at: Optional[datetime] = None


class Directory(BaseModel):
    id: Optional[str] = None

    attribute_mappings: Optional[AttributeMappings] = None

    directory_endpoint: Optional[str] = None

    directory_provider: Optional[int] = None

    directory_type: Optional[int] = None

    email: Optional[str] = None

    enabled: Optional[bool] = None

    groups_tracked: Optional[str] = None

    last_synced_at: Optional[datetime] = None

    name: Optional[str] = None

    organization_id: Optional[str] = None

    role_assignments: Optional[RoleAssignments] = None

    secrets: Optional[List[Secret]] = None

    stats: Optional[Stats] = None

    status: Optional[str] = None

    total_groups: Optional[int] = None

    total_users: Optional[int] = None
