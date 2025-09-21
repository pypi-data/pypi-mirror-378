# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .update_default_role_param import UpdateDefaultRoleParam

__all__ = ["RoleUpdateDefaultParams"]


class RoleUpdateDefaultParams(TypedDict, total=False):
    default_creator: UpdateDefaultRoleParam

    default_creator_role: str

    default_member: UpdateDefaultRoleParam

    default_member_role: str
