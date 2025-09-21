# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ClientListParams"]


class ClientListParams(TypedDict, total=False):
    page_size: int
    """Maximum number of clients to return per page"""

    page_token: str
    """Pagination token from the previous response"""
