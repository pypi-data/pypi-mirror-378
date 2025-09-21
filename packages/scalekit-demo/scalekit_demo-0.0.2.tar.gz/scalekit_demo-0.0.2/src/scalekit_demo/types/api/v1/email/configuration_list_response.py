# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .email_server import EmailServer

__all__ = ["ConfigurationListResponse"]


class ConfigurationListResponse(BaseModel):
    default_from_address: Optional[str] = None

    default_from_name: Optional[str] = None

    email_server_selected: Optional[int] = None

    server: Optional[EmailServer] = None
