# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["UserManagementUpdateUserManagementParams"]


class UserManagementUpdateUserManagementParams(TypedDict, total=False):
    allow_duplicate_user_identities: bool

    allow_multiple_memberships: bool

    allow_organization_signup: bool

    block_disposable_email_domains: bool
    """Indicates whether disposable email domains are blocked for user signup/invite."""

    block_public_email_domains: bool
    """Indicates whether public email domains are blocked for user signup/invite."""

    enable_max_users_limit: bool

    invitation_expiry: int

    max_users_limit: int

    org_user_relationship: int
