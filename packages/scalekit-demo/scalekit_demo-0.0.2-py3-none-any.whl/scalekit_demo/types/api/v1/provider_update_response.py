# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .provider import Provider
from ...._models import BaseModel

__all__ = ["ProviderUpdateResponse"]


class ProviderUpdateResponse(BaseModel):
    provider: Optional[Provider] = None
