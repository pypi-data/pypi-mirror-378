# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .organizations.clients.client_secret import ClientSecret

__all__ = ["Client"]


class Client(BaseModel):
    id: Optional[str] = None

    back_channel_logout_uris: Optional[List[str]] = None

    create_time: Optional[datetime] = None

    default_redirect_uri: Optional[str] = None

    initiate_login_uri: Optional[str] = None

    key_id: Optional[str] = FieldInfo(alias="keyId", default=None)

    post_login_uris: Optional[List[str]] = None

    post_logout_redirect_uris: Optional[List[str]] = None

    redirect_uris: Optional[List[str]] = None

    secrets: Optional[List[ClientSecret]] = None

    update_time: Optional[datetime] = None
