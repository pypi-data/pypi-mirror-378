# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from .m2_m_client import M2MClient

__all__ = ["ClientUpdateResponse"]


class ClientUpdateResponse(BaseModel):
    client: Optional[M2MClient] = None
