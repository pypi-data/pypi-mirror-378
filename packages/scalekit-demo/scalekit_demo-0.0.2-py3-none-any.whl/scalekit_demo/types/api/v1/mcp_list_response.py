# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .mcp import Mcp
from ...._models import BaseModel

__all__ = ["McpListResponse"]


class McpListResponse(BaseModel):
    mcps: Optional[List[Mcp]] = None
