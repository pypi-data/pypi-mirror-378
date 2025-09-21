# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ProviderListParams"]


class ProviderListParams(TypedDict, total=False):
    identifier: str

    page_size: int

    page_token: str
