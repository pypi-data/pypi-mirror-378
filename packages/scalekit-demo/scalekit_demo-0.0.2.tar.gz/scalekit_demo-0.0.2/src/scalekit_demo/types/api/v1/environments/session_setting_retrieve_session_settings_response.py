# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .session_settings import SessionSettings

__all__ = ["SessionSettingRetrieveSessionSettingsResponse"]


class SessionSettingRetrieveSessionSettingsResponse(BaseModel):
    session_settings: Optional[SessionSettings] = None
