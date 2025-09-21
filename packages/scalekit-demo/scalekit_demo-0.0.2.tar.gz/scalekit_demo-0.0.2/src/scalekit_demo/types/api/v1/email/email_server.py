# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel
from .smtp_server_settings import SmtpServerSettings

__all__ = ["EmailServer"]


class EmailServer(BaseModel):
    id: Optional[str] = None

    enabled: Optional[bool] = None

    provider: Optional[int] = None

    smtp_settings: Optional[SmtpServerSettings] = None

    updated_at: Optional[datetime] = None
