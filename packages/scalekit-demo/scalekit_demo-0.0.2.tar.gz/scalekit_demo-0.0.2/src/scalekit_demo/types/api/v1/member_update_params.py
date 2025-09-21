# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .update_user_profile_param import UpdateUserProfileParam

__all__ = ["MemberUpdateParams"]


class MemberUpdateParams(TypedDict, total=False):
    first_name: str

    last_name: str

    metadata: Dict[str, str]

    role: int

    user_profile: UpdateUserProfileParam
