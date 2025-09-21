# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["TotpEnableResponse"]


class TotpEnableResponse(BaseModel):
    id: Optional[str] = None

    backup_codes: Optional[List[str]] = None
