# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel

__all__ = ["UserManagement"]


class UserManagement(BaseModel):
    allow_duplicate_user_identities: Optional[bool] = None

    allow_multiple_memberships: Optional[bool] = None

    allow_organization_signup: Optional[bool] = None

    block_disposable_email_domains: Optional[bool] = None
    """Indicates whether disposable email domains are blocked for user signup/invite."""

    block_public_email_domains: Optional[bool] = None
    """Indicates whether public email domains are blocked for user signup/invite."""

    enable_max_users_limit: Optional[bool] = None

    invitation_expiry: Optional[int] = None

    max_users_limit: Optional[int] = None

    org_user_relationship: Optional[int] = None
