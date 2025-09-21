# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ......_models import BaseModel
from .directory_group import DirectoryGroup

__all__ = ["ListDirectoryGroupsResponse"]


class ListDirectoryGroupsResponse(BaseModel):
    groups: Optional[List[DirectoryGroup]] = None

    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None
