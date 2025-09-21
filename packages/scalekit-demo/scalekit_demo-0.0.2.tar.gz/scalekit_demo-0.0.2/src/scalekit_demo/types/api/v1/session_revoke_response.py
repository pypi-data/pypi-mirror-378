# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .session_details import SessionDetails

__all__ = ["SessionRevokeResponse"]


class SessionRevokeResponse(BaseModel):
    revoked_session: Optional[SessionDetails] = None
