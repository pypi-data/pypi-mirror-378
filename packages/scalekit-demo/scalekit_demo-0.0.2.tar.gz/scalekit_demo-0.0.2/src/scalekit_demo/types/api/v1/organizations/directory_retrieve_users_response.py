# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ....._models import BaseModel
from .directories.directory_group import DirectoryGroup

__all__ = ["DirectoryRetrieveUsersResponse", "User"]


class User(BaseModel):
    id: Optional[str] = None

    email: Optional[str] = None

    emails: Optional[List[str]] = None

    family_name: Optional[str] = None

    given_name: Optional[str] = None

    groups: Optional[List[DirectoryGroup]] = None

    preferred_username: Optional[str] = None

    updated_at: Optional[datetime] = None

    user_detail: Optional[object] = None


class DirectoryRetrieveUsersResponse(BaseModel):
    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None

    users: Optional[List[User]] = None
