# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SecretUpdateParams"]


class SecretUpdateParams(TypedDict, total=False):
    client_id: Required[str]

    mask: str
    """Fields to update (system-controlled parameter)"""

    status: int
    """Status of the secret (active or inactive)"""
