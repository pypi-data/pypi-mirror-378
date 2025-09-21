# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .organization_session_settings import OrganizationSessionSettings

__all__ = ["SessionSettingRetrieveSessionSettingsResponse"]


class SessionSettingRetrieveSessionSettingsResponse(BaseModel):
    environment_id: Optional[str] = None

    organization_id: Optional[str] = None

    session_settings: Optional[OrganizationSessionSettings] = None
