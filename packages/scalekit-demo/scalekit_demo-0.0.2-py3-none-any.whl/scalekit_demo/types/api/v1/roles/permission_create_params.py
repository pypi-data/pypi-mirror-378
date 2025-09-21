# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo

__all__ = ["PermissionCreateParams"]


class PermissionCreateParams(TypedDict, total=False):
    permission_names: SequenceNotStr[str]

    body_role_name: Annotated[str, PropertyInfo(alias="role_name")]
