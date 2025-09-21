# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["TotpRegistrationParams"]


class TotpRegistrationParams(TypedDict, total=False):
    create_time: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """Created Time"""

    id: str
    """Id"""

    account_name: str

    update_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Updated time"""

    user_id: str
