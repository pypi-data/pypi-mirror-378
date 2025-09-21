# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .location import Location
from ...._models import BaseModel

__all__ = ["SessionDetails"]


class SessionDetails(BaseModel):
    absolute_expires_at: Optional[datetime] = None

    authenticated_organizations: Optional[List[str]] = None

    created_at: Optional[datetime] = None

    expired_at: Optional[datetime] = None

    idle_expires_at: Optional[datetime] = None

    initial_browser: Optional[str] = None

    initial_browser_version: Optional[str] = None

    initial_device_type: Optional[str] = None

    initial_ip: Optional[str] = None

    initial_location: Optional[Location] = None

    initial_os: Optional[str] = None

    initial_os_version: Optional[str] = None

    initial_user_agent: Optional[str] = None

    latest_browser: Optional[str] = None

    latest_browser_version: Optional[str] = None

    latest_device_type: Optional[str] = None

    latest_ip: Optional[str] = None

    latest_location: Optional[Location] = None

    latest_os: Optional[str] = None

    latest_os_version: Optional[str] = None

    latest_user_agent: Optional[str] = None

    logout_at: Optional[datetime] = None

    organization_id: Optional[str] = None

    session_id: Optional[str] = None

    status: Optional[str] = None

    updated_at: Optional[datetime] = None

    user_id: Optional[str] = None
