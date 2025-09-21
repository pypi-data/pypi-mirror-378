# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["RoleParam", "Permission"]


class Permission(TypedDict, total=False):
    id: str

    create_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    description: str

    name: str

    role_name: str

    update_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]


class RoleParam(TypedDict, total=False):
    default_creator: bool

    default_member: bool

    dependent_roles_count: int

    description: str

    display_name: str

    extends: str

    is_org_role: bool

    name: str

    permissions: Iterable[Permission]
