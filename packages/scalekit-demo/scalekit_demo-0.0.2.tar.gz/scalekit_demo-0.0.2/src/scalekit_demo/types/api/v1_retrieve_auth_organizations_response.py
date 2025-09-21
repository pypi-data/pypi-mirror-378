# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .v1.organization import Organization

__all__ = ["V1RetrieveAuthOrganizationsResponse", "User"]


class User(BaseModel):
    email: Optional[str] = None

    first_name: Optional[str] = None

    last_name: Optional[str] = None


class V1RetrieveAuthOrganizationsResponse(BaseModel):
    intent: Optional[int] = None

    organizations: Optional[List[Organization]] = None

    user: Optional[User] = None
