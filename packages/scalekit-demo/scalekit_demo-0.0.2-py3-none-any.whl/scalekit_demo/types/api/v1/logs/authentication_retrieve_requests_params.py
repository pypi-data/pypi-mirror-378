# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["AuthenticationRetrieveRequestsParams"]


class AuthenticationRetrieveRequestsParams(TypedDict, total=False):
    email: str

    end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    page_size: int

    page_token: str

    start_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    status: str
