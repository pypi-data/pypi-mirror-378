# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ConnectionCreateParams", "Flags"]


class ConnectionCreateParams(TypedDict, total=False):
    flags: Flags

    key_id: str

    provider: int

    provider_key: str

    type: int


class Flags(TypedDict, total=False):
    is_app: bool

    is_login: bool
