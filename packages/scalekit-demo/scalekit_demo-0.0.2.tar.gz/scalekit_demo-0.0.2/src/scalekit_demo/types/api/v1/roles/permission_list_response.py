# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel
from ..permission import Permission

__all__ = ["PermissionListResponse"]


class PermissionListResponse(BaseModel):
    permissions: Optional[List[Permission]] = None
