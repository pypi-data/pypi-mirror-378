# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .scope import Scope
from ....._models import BaseModel

__all__ = ["ListScopesResponse"]


class ListScopesResponse(BaseModel):
    scopes: Optional[List[Scope]] = None
