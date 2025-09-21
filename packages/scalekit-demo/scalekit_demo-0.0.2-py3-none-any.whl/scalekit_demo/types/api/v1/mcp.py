# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["Mcp", "ToolMapping"]


class ToolMapping(BaseModel):
    connection_name: Optional[str] = None

    status: Optional[str] = None

    tool_names: Optional[List[str]] = None


class Mcp(BaseModel):
    id: Optional[str] = None

    connected_account_identifier: Optional[str] = None

    tool_mappings: Optional[List[ToolMapping]] = None

    url: Optional[str] = None
