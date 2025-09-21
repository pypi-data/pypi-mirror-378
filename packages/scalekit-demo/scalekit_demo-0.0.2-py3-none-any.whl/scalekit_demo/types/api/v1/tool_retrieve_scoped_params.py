# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["ToolRetrieveScopedParams", "Filter"]


class ToolRetrieveScopedParams(TypedDict, total=False):
    filter: Filter

    identifier: str

    page_size: int

    page_token: str


class Filter(TypedDict, total=False):
    connection_names: SequenceNotStr[str]

    providers: SequenceNotStr[str]

    tool_names: SequenceNotStr[str]
