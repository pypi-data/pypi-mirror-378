# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["AuthenticationRetrieveRequestsResponse", "AuthRequest", "AuthRequestConnectionDetail"]


class AuthRequestConnectionDetail(BaseModel):
    connection_id: Optional[str] = None

    connection_provider: Optional[str] = None

    connection_type: Optional[str] = None

    organization_id: Optional[str] = None


class AuthRequest(BaseModel):
    auth_request_id: Optional[str] = None

    connection_details: Optional[List[AuthRequestConnectionDetail]] = None

    connection_id: Optional[str] = None

    connection_provider: Optional[str] = None

    connection_type: Optional[str] = None

    email: Optional[str] = None

    environment_id: Optional[str] = None

    organization_id: Optional[str] = None

    status: Optional[str] = None

    timestamp: Optional[datetime] = None

    workflow: Optional[str] = None


class AuthenticationRetrieveRequestsResponse(BaseModel):
    auth_requests: Optional[List[AuthRequest]] = FieldInfo(alias="authRequests", default=None)

    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None
