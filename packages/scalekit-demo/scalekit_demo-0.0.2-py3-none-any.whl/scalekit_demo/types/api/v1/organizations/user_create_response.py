# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel
from ..connections.user import User

__all__ = ["UserCreateResponse"]


class UserCreateResponse(BaseModel):
    user: Optional[User] = None
