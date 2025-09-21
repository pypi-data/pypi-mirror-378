# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["V1RetrieveResponse"]


class V1RetrieveResponse(BaseModel):
    domains: Optional[List[str]] = None
