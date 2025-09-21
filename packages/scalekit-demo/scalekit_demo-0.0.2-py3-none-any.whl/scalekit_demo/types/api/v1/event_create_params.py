# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["EventCreateParams"]


class EventCreateParams(TypedDict, total=False):
    page_size: int

    page_token: str

    auth_request_id: str

    end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    event_types: SequenceNotStr[str]

    organization_id: str

    source: int

    start_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
