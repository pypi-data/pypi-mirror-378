# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["SmtpServerSettings"]


class SmtpServerSettings(BaseModel):
    from_email: Optional[str] = None

    from_name: Optional[str] = None

    host: Optional[str] = None

    port: Optional[str] = None

    username: Optional[str] = None
