# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .attribute_mappings import AttributeMappings

__all__ = ["DirectoryUpdateAttributesResponse"]


class DirectoryUpdateAttributesResponse(BaseModel):
    attribute_mappings: Optional[AttributeMappings] = None
