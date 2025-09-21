# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ....._types import SequenceNotStr

__all__ = ["RoleUpdateParams"]


class RoleUpdateParams(TypedDict, total=False):
    org_id: Required[str]

    description: str

    display_name: str

    extends: str

    permissions: SequenceNotStr[str]
