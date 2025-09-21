# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .totp_registration import TotpRegistration

__all__ = ["TotpRegistrationResponse"]


class TotpRegistrationResponse(BaseModel):
    totp_registration: Optional[TotpRegistration] = None
