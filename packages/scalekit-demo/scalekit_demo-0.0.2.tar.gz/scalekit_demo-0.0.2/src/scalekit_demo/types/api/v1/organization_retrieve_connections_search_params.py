# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["OrganizationRetrieveConnectionsSearchParams"]


class OrganizationRetrieveConnectionsSearchParams(TypedDict, total=False):
    connection_type: int

    enabled: bool

    page_size: int

    page_token: str

    provider: str

    query: str

    status: int
