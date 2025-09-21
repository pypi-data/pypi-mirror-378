# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr
from .list_value_param import ListValueParam

__all__ = ["ProviderCreateParams"]


class ProviderCreateParams(TypedDict, total=False):
    auth_patterns: ListValueParam
    """`ListValue` is a wrapper around a repeated field of values.

    The JSON representation for `ListValue` is JSON array.
    """

    categories: SequenceNotStr[str]

    coming_soon: bool

    description: str

    display_name: str

    display_priority: int

    icon_src: str

    identifier: str
