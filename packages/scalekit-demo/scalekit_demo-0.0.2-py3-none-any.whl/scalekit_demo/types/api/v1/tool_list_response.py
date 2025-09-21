# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .tool import Tool
from ...._models import BaseModel

__all__ = ["ToolListResponse"]


class ToolListResponse(BaseModel):
    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    tool_names: Optional[List[str]] = None

    tools: Optional[List[Tool]] = None

    total_size: Optional[int] = None
