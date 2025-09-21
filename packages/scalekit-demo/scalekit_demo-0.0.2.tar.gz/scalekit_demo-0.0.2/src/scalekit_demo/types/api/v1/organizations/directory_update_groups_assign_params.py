# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo

__all__ = ["DirectoryUpdateGroupsAssignParams"]


class DirectoryUpdateGroupsAssignParams(TypedDict, total=False):
    path_organization_id: Required[Annotated[str, PropertyInfo(alias="organization_id")]]

    body_id: Annotated[str, PropertyInfo(alias="id")]

    external_ids: SequenceNotStr[str]

    body_organization_id: Annotated[str, PropertyInfo(alias="organization_id")]
