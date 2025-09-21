# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["ServerUpdateServerIDEnableResponse"]


class ServerUpdateServerIDEnableResponse(BaseModel):
    active_server_id: Optional[str] = None

    last_active_server_id: Optional[str] = None
