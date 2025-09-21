# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .environments.scope import Scope

__all__ = ["ScopeUpdateResponse"]


class ScopeUpdateResponse(BaseModel):
    scope: Optional[Scope] = None
