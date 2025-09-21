# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

from ...organizations.role_param import RoleParam

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    organization_id: Required[str]

    external_id: str

    metadata: Dict[str, str]

    roles: Iterable[RoleParam]
