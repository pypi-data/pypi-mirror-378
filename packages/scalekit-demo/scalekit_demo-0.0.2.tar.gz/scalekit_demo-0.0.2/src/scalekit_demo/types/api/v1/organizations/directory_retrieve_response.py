# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .directory import Directory
from ....._models import BaseModel

__all__ = ["DirectoryRetrieveResponse"]


class DirectoryRetrieveResponse(BaseModel):
    directory: Optional[Directory] = None
