# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["V1ExecuteToolResponse"]


class V1ExecuteToolResponse(BaseModel):
    data: Optional[object] = None

    execution_id: Optional[str] = None
