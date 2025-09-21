# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .connected_account import ConnectedAccount

__all__ = ["ConnectedAccountRetrieveAuthResponse"]


class ConnectedAccountRetrieveAuthResponse(BaseModel):
    connected_account: Optional[ConnectedAccount] = None
