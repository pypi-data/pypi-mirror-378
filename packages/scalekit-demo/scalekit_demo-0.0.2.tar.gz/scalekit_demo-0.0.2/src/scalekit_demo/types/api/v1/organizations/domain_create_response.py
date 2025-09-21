# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .domain import Domain
from ....._models import BaseModel

__all__ = ["DomainCreateResponse"]


class DomainCreateResponse(BaseModel):
    domain: Optional[Domain] = None
