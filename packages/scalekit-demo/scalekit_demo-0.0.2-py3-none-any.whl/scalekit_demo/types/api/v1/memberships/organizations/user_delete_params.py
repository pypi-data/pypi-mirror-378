# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["UserDeleteParams"]


class UserDeleteParams(TypedDict, total=False):
    organization_id: Required[str]

    cascade: bool

    external_id: str
