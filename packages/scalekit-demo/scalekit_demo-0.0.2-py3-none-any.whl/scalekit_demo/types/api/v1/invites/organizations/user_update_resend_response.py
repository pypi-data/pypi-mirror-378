# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ......_models import BaseModel

__all__ = ["UserUpdateResendResponse", "Invite"]


class Invite(BaseModel):
    created_at: Optional[datetime] = None

    expires_at: Optional[datetime] = None

    inviter_email: Optional[str] = None

    organization_id: Optional[str] = None

    resent_at: Optional[datetime] = None

    resent_count: Optional[int] = None

    status: Optional[str] = None

    user_id: Optional[str] = None


class UserUpdateResendResponse(BaseModel):
    invite: Optional[Invite] = None
