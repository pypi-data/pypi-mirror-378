# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["OrganizationSessionSettings"]


class OrganizationSessionSettings(BaseModel):
    absolute_session_timeout: Optional[int] = None

    idle_session_enabled: Optional[bool] = None

    idle_session_timeout: Optional[int] = None

    session_management_enabled: Optional[bool] = None
