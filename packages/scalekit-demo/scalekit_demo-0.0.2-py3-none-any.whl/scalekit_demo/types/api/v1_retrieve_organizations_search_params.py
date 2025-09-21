# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["V1RetrieveOrganizationsSearchParams"]


class V1RetrieveOrganizationsSearchParams(TypedDict, total=False):
    page_size: int

    page_token: str

    query: str
