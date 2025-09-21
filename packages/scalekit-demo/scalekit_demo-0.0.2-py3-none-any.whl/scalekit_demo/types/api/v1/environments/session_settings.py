# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["SessionSettings"]


class SessionSettings(BaseModel):
    absolute_session_timeout: Optional[int] = None

    access_token_expiry: Optional[int] = None

    client_access_token_expiry: Optional[int] = None

    cookie_custom_domain: Optional[str] = None

    cookie_persistence_type: Optional[int] = None

    cookie_same_site_setting: Optional[int] = None

    idle_session_enabled: Optional[bool] = None

    idle_session_timeout: Optional[int] = None

    session_management_enabled: Optional[bool] = None
