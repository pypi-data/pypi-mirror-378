# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .directory import Directory
from ....._models import BaseModel

__all__ = ["DirectoryListResponse"]


class DirectoryListResponse(BaseModel):
    directories: Optional[List[Directory]] = None
