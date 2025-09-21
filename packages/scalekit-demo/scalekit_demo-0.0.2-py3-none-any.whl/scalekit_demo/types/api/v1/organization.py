# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["Organization"]


class Organization(BaseModel):
    id: Optional[str] = None

    invitation_accepted_at: Optional[datetime] = None

    invitation_created_at: Optional[datetime] = None

    invitation_expires_at: Optional[datetime] = None

    invitation_inviter_email: Optional[str] = None

    membership_status: Optional[str] = None

    name: Optional[str] = None
