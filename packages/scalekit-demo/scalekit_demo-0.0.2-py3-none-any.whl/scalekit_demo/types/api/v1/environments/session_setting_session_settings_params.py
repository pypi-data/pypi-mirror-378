# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SessionSettingSessionSettingsParams"]


class SessionSettingSessionSettingsParams(TypedDict, total=False):
    absolute_session_timeout: int

    access_token_expiry: int

    client_access_token_expiry: int

    cookie_custom_domain: str

    cookie_persistence_type: int

    cookie_same_site_setting: int

    idle_session_enabled: bool

    idle_session_timeout: int

    session_management_enabled: bool
