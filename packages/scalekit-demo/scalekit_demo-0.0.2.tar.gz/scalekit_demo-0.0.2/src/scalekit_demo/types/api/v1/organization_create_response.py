# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .organization import Organization

__all__ = ["OrganizationCreateResponse"]


class OrganizationCreateResponse(BaseModel):
    organization: Optional[Organization] = None
