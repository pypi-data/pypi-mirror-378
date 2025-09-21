# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["V1RetrieveConnectedAccountsSearchParams"]


class V1RetrieveConnectedAccountsSearchParams(TypedDict, total=False):
    connection_id: str

    page_size: int

    page_token: str

    query: str
