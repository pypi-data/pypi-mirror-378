# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .scope import Scope
from ....._models import BaseModel

__all__ = ["CreateScopeResponse"]


class CreateScopeResponse(BaseModel):
    scope: Optional[Scope] = None
