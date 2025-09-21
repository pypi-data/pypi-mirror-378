# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel
from .email_server import EmailServer

__all__ = ["ServerListResponse"]


class ServerListResponse(BaseModel):
    servers: Optional[List[EmailServer]] = None
