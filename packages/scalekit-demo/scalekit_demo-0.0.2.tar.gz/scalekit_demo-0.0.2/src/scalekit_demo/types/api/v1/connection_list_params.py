# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ConnectionListParams"]


class ConnectionListParams(TypedDict, total=False):
    domain: str

    include: str

    organization_id: str
