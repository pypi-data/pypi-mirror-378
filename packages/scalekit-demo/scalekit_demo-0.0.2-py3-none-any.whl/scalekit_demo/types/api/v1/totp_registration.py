# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["TotpRegistration"]


class TotpRegistration(BaseModel):
    create_time: datetime
    """Created Time"""

    id: Optional[str] = None
    """Id"""

    account_name: Optional[str] = None

    qr_code_uri: Optional[str] = None

    update_time: Optional[datetime] = None
    """Updated time"""

    user_id: Optional[str] = None
