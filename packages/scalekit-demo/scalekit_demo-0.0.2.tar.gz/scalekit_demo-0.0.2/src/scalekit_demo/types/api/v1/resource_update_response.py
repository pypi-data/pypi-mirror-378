# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .oauth.resource import Resource

__all__ = ["ResourceUpdateResponse"]


class ResourceUpdateResponse(BaseModel):
    resource: Optional[Resource] = None
