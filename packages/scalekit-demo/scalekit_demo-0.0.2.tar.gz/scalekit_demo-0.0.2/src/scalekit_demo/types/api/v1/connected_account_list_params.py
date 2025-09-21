# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ConnectedAccountListParams"]


class ConnectedAccountListParams(TypedDict, total=False):
    connector: str

    identifier: str

    organization_id: str

    page_size: int

    page_token: str

    provider: str

    query: str

    user_id: str
