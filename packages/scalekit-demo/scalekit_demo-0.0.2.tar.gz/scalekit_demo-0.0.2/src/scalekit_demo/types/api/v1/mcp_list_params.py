# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["McpListParams", "Filter"]


class McpListParams(TypedDict, total=False):
    filter: Filter


class Filter(TypedDict, total=False):
    connected_account_identifier: str

    link_token: str
