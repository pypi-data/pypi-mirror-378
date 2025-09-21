# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["DirectoryUpdateAttributesParams", "Attribute"]


class DirectoryUpdateAttributesParams(TypedDict, total=False):
    organization_id: Required[str]

    attributes: Iterable[Attribute]


class Attribute(TypedDict, total=False):
    key: str

    map_to: str
