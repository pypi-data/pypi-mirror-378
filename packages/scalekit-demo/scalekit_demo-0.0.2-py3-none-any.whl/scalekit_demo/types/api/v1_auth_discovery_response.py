# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .auth_method import AuthMethod

__all__ = ["V1AuthDiscoveryResponse"]


class V1AuthDiscoveryResponse(BaseModel):
    auth_method: Optional[AuthMethod] = None
