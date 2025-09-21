# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RoleDeleteParams"]


class RoleDeleteParams(TypedDict, total=False):
    org_id: Required[str]

    reassign_role_name: str
