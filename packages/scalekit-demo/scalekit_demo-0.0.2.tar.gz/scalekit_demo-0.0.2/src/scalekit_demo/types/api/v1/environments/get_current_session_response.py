# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["GetCurrentSessionResponse"]


class GetCurrentSessionResponse(BaseModel):
    access_token_expiry: Optional[datetime] = None

    email: Optional[str] = None

    organization_id: Optional[str] = None

    session_expiry: Optional[datetime] = None

    subject: Optional[str] = None
