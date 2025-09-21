# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel
from .user_management import UserManagement

__all__ = ["UserManagementUpdateUserManagementResponse"]


class UserManagementUpdateUserManagementResponse(BaseModel):
    environment_id: Optional[str] = None

    user_management: Optional[UserManagement] = None
