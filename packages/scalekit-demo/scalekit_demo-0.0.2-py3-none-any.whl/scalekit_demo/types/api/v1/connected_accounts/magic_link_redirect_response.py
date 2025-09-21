# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["MagicLinkRedirectResponse"]


class MagicLinkRedirectResponse(BaseModel):
    expiry: Optional[datetime] = None

    redirect_to: Optional[str] = None
