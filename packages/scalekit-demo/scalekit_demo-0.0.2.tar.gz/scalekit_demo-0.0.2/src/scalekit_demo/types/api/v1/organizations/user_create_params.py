# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from ..memberships.organizations.create_membership_param import CreateMembershipParam

__all__ = ["UserCreateParams", "UserProfile"]


class UserCreateParams(TypedDict, total=False):
    send_invitation_email: bool

    email: str

    external_id: str

    membership: CreateMembershipParam

    metadata: Dict[str, str]

    user_profile: UserProfile


class UserProfile(TypedDict, total=False):
    custom_attributes: Dict[str, str]

    first_name: str

    last_name: str

    locale: str

    metadata: Dict[str, str]

    name: str

    phone_number: str
