# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from ..oauth.resource import Resource
from ..organizations.m2_m_client import M2MClient

__all__ = ["ClientRetrieveResponse"]


class ClientRetrieveResponse(BaseModel):
    client: Optional[M2MClient] = None

    resource: Optional[Resource] = None
