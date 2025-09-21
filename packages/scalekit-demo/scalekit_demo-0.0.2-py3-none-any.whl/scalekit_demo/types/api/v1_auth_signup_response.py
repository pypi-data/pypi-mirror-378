# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["V1AuthSignupResponse"]


class V1AuthSignupResponse(BaseModel):
    organization_id: Optional[str] = None

    organization_name: Optional[str] = None
