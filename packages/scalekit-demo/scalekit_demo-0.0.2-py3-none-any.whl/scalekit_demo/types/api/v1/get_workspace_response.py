# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from ..workspace import Workspace

__all__ = ["GetWorkspaceResponse"]


class GetWorkspaceResponse(BaseModel):
    workspace: Optional[Workspace] = None
