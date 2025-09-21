# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["GroupUpdateRolesAssignParams", "Assignment"]


class GroupUpdateRolesAssignParams(TypedDict, total=False):
    organization_id: Required[str]

    assignments: Iterable[Assignment]


class Assignment(TypedDict, total=False):
    group_id: str

    role_id: str

    role_name: str
