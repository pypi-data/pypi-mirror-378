# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ScopeCreateParams"]


class ScopeCreateParams(TypedDict, total=False):
    env_id: str

    description: str

    name: str
