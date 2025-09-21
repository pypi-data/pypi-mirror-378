# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .workspace import Workspace

__all__ = ["V1SignupResponse"]


class V1SignupResponse(BaseModel):
    link: Optional[str] = None

    workspace: Optional[Workspace] = None
