# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

from ..._types import SequenceNotStr

__all__ = ["V1FetchBulkParams", "Resource"]


class V1FetchBulkParams(TypedDict, total=False):
    resources: Iterable[Resource]


class Resource(TypedDict, total=False):
    identifiers: SequenceNotStr[str]

    type: int
