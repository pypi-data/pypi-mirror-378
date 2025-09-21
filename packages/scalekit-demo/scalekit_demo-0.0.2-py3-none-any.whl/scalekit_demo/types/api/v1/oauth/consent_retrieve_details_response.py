# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .resource import Resource
from ....._models import BaseModel
from ..connections.user import User

__all__ = ["ConsentRetrieveDetailsResponse", "Application", "Client", "Scope"]


class Application(BaseModel):
    id: Optional[str] = None

    access_token_expiry: Optional[str] = None

    application_type: Optional[int] = None

    create_time: Optional[datetime] = None

    description: Optional[str] = None

    disable_dynamic_client_registration: Optional[bool] = None

    logo_uri: Optional[str] = None

    name: Optional[str] = None

    provider: Optional[str] = None

    refresh_token_expiry: Optional[str] = None

    resource_id: Optional[str] = None

    update_time: Optional[datetime] = None


class Client(BaseModel):
    name: Optional[str] = None

    privacy_uri: Optional[str] = None

    tos_uri: Optional[str] = None


class Scope(BaseModel):
    description: Optional[str] = None

    name: Optional[str] = None


class ConsentRetrieveDetailsResponse(BaseModel):
    application: Optional[Application] = None
    """for backward compatibility"""

    client: Optional[Client] = None

    resource: Optional[Resource] = None

    scopes: Optional[List[Scope]] = None

    user: Optional[User] = None
