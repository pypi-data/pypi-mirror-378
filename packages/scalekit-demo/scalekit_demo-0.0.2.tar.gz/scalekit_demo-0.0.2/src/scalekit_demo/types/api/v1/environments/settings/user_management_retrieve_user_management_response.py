# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel
from .user_management import UserManagement

__all__ = ["UserManagementRetrieveUserManagementResponse"]


class UserManagementRetrieveUserManagementResponse(BaseModel):
    user_management: Optional[UserManagement] = None
