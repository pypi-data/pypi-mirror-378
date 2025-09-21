# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .v1.tool import Tool
from ..._models import BaseModel

__all__ = ["V1ToolsSetDefaultResponse"]


class V1ToolsSetDefaultResponse(BaseModel):
    tool: Optional[Tool] = None
