# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["SendPasswordlessResponse"]


class SendPasswordlessResponse(BaseModel):
    auth_request_id: Optional[str] = None

    expires_at: Optional[str] = None

    expires_in: Optional[int] = None

    passwordless_type: Optional[int] = None
