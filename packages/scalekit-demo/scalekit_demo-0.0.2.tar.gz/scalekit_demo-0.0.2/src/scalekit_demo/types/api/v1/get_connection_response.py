# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .connection import Connection

__all__ = ["GetConnectionResponse"]


class GetConnectionResponse(BaseModel):
    connection: Optional[Connection] = None
