# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel
from .organization_user_management_settings import OrganizationUserManagementSettings

__all__ = ["UsermanagementPatchAllResponse"]


class UsermanagementPatchAllResponse(BaseModel):
    settings: Optional[OrganizationUserManagementSettings] = None
