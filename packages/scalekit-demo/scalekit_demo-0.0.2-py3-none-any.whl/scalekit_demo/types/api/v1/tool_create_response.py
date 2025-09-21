# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .tool import Tool
from ...._models import BaseModel

__all__ = ["ToolCreateResponse"]


class ToolCreateResponse(BaseModel):
    tool: Optional[Tool] = None
