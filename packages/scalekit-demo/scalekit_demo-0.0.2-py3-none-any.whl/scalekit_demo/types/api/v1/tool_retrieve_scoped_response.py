# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from . import tool as _tool
from ...._models import BaseModel

__all__ = ["ToolRetrieveScopedResponse", "Tool"]


class Tool(BaseModel):
    connected_account_id: Optional[str] = None

    identifier: Optional[str] = None

    tool: Optional[_tool.Tool] = None


class ToolRetrieveScopedResponse(BaseModel):
    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    tools: Optional[List[Tool]] = None

    total_size: Optional[int] = None
