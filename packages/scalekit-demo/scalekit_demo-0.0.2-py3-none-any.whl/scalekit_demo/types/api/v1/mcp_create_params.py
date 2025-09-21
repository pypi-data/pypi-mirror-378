# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["McpCreateParams", "ToolMapping"]


class McpCreateParams(TypedDict, total=False):
    connected_account_identifier: str

    tool_mappings: Iterable[ToolMapping]


class ToolMapping(TypedDict, total=False):
    connection_name: str

    tool_names: SequenceNotStr[str]
