# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SessionSettingUpdateSessionSettingsParams"]


class SessionSettingUpdateSessionSettingsParams(TypedDict, total=False):
    environment_id: str

    absolute_session_timeout: int

    idle_session_enabled: bool

    idle_session_timeout: int

    session_management_enabled: bool
