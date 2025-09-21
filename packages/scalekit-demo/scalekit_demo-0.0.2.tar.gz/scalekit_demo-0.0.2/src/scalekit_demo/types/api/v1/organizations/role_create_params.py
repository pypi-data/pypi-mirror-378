# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ....._types import SequenceNotStr

__all__ = ["RoleCreateParams"]


class RoleCreateParams(TypedDict, total=False):
    description: str

    display_name: str

    extends: str

    name: str

    permissions: SequenceNotStr[str]
