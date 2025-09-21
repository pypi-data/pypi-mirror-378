# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ....._models import BaseModel
from ..environments.scope import Scope

__all__ = ["Resource"]


class Resource(BaseModel):
    id: Optional[str] = None

    access_token_expiry: Optional[str] = None

    create_time: Optional[datetime] = None

    description: Optional[str] = None

    disable_dynamic_client_registration: Optional[bool] = None

    logo_uri: Optional[str] = None

    name: Optional[str] = None

    protected_metadata: Optional[object] = None

    protected_metadata_uri: Optional[str] = None

    provider: Optional[str] = None

    refresh_token_expiry: Optional[str] = None

    resource_id: Optional[str] = None

    resource_type: Optional[int] = None

    resource_uri: Optional[str] = None

    scopes: Optional[List[Scope]] = None

    update_time: Optional[datetime] = None
