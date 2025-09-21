# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .email_server import EmailServer

__all__ = ["GetEmailServerResponse"]


class GetEmailServerResponse(BaseModel):
    server: Optional[EmailServer] = None
