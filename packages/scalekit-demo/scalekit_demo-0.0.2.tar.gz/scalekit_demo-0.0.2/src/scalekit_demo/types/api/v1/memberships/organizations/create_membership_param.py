# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import TypedDict

from ...organizations.role_param import RoleParam

__all__ = ["CreateMembershipParam"]


class CreateMembershipParam(TypedDict, total=False):
    inviter_email: str

    metadata: Dict[str, str]

    roles: Iterable[RoleParam]
