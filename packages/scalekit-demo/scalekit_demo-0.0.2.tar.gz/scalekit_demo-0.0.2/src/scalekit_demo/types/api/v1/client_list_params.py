# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ClientListParams"]


class ClientListParams(TypedDict, total=False):
    include_plain_secret: bool
    """Controls whether plain secret values are included in the response"""
