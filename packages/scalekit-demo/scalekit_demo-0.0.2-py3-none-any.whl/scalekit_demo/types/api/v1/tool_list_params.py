# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["ToolListParams", "Filter"]


class ToolListParams(TypedDict, total=False):
    filter: Filter

    page_size: int

    page_token: str


class Filter(TypedDict, total=False):
    identifier: str

    provider: str

    query: str

    summary: bool

    tool_name: SequenceNotStr[str]
