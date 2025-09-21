# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["V1FetchBulkResponse"]


class V1FetchBulkResponse(BaseModel):
    resources: Optional[Dict[str, object]] = None
