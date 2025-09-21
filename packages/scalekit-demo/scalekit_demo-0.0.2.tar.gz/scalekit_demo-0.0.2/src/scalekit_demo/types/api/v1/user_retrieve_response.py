# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .connections.user import User

__all__ = ["UserRetrieveResponse"]


class UserRetrieveResponse(BaseModel):
    user: Optional[User] = None
