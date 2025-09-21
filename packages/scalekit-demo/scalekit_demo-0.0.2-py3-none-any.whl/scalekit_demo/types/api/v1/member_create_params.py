# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["MemberCreateParams", "UserProfile"]


class MemberCreateParams(TypedDict, total=False):
    id: str

    create_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    email: str

    first_name: str

    last_name: str

    metadata: Dict[str, str]

    role: int

    update_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    user_profile: UserProfile

    workspace_id: str


class UserProfile(TypedDict, total=False):
    custom_attributes: Dict[str, str]

    first_name: str

    last_name: str

    locale: str

    metadata: Dict[str, str]

    name: str

    phone_number: str
