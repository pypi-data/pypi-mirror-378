# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from ...._models import BaseModel
from .organizations.role import Role

__all__ = ["Member", "Organization", "UserProfile"]


class Organization(BaseModel):
    accepted_at: Optional[datetime] = None

    created_at: Optional[datetime] = None

    display_name: Optional[str] = None

    expires_at: Optional[datetime] = None

    inviter_email: Optional[str] = None

    join_time: Optional[datetime] = None

    membership_status: Optional[int] = None

    metadata: Optional[Dict[str, str]] = None

    name: Optional[str] = None

    organization_id: Optional[str] = None

    roles: Optional[List[Role]] = None


class UserProfile(BaseModel):
    id: Optional[str] = None

    custom_attributes: Optional[Dict[str, str]] = None

    email_verified: Optional[bool] = None

    first_name: Optional[str] = None

    last_name: Optional[str] = None

    locale: Optional[str] = None

    metadata: Optional[Dict[str, str]] = None

    name: Optional[str] = None

    phone_number: Optional[str] = None


class Member(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    email: Optional[str] = None

    external_id: Optional[str] = None

    first_name: Optional[str] = None

    last_name: Optional[str] = None

    metadata: Optional[Dict[str, str]] = None

    organizations: Optional[List[Organization]] = None

    role: Optional[int] = None

    update_time: Optional[datetime] = None

    user_profile: Optional[UserProfile] = None

    workspace_id: Optional[str] = None
