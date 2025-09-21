# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .organization import Organization

__all__ = ["GetOrganizationResponse"]


class GetOrganizationResponse(BaseModel):
    organization: Optional[Organization] = None
