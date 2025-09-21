# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .session_settings import SessionSettings

__all__ = ["SessionSettingUpdateSessionSettingsResponse"]


class SessionSettingUpdateSessionSettingsResponse(BaseModel):
    environment_id: Optional[str] = None

    session_settings: Optional[SessionSettings] = None
