# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["DirectoryUpdateParams", "Group", "Mapping"]


class DirectoryUpdateParams(TypedDict, total=False):
    organization_id: Required[str]

    directory_provider: int

    directory_type: int

    enabled: bool

    groups: Iterable[Group]

    mappings: Iterable[Mapping]

    name: str

    status: int


class Group(TypedDict, total=False):
    display_name: str

    email: str

    external_id: str


class Mapping(TypedDict, total=False):
    display_name: str

    key: str

    map_to: str
