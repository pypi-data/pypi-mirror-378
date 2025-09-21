# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DirectoryRetrieveUsersParams"]


class DirectoryRetrieveUsersParams(TypedDict, total=False):
    organization_id: Required[str]

    directory_group_id: str

    include_detail: bool

    page_size: int

    page_token: str

    updated_after: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
