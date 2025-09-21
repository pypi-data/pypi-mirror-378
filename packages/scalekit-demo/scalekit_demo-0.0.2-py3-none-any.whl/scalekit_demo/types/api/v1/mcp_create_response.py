# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .mcp import Mcp
from ...._models import BaseModel

__all__ = ["McpCreateResponse"]


class McpCreateResponse(BaseModel):
    mcp: Optional[Mcp] = None
