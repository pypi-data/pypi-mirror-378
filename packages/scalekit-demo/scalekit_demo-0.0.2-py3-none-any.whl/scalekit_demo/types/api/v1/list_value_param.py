# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

__all__ = ["ListValueParam"]


class ListValueParam(TypedDict, total=False):
    values: Iterable[object]
    """Repeated field of dynamically typed values."""
