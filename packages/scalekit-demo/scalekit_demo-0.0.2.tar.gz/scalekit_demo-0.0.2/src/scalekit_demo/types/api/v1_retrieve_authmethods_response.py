# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .auth_method import AuthMethod

__all__ = ["V1RetrieveAuthmethodsResponse"]


class V1RetrieveAuthmethodsResponse(BaseModel):
    auth_methods: Optional[List[AuthMethod]] = None
