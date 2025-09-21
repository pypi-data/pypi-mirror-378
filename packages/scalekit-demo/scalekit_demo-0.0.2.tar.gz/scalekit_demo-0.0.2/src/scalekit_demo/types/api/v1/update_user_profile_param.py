# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["UpdateUserProfileParam"]


class UpdateUserProfileParam(TypedDict, total=False):
    custom_attributes: Dict[str, str]

    first_name: str

    last_name: str

    locale: str

    metadata: Dict[str, str]

    name: str

    phone_number: str
