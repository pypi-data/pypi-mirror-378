# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo
from .update_user_profile_param import UpdateUserProfileParam

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    query_external_id: Annotated[str, PropertyInfo(alias="external_id")]

    body_external_id: Annotated[str, PropertyInfo(alias="external_id")]

    metadata: Dict[str, str]

    user_profile: UpdateUserProfileParam
