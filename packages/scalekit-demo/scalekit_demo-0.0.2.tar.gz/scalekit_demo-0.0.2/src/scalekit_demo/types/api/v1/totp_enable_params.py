# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["TotpEnableParams"]


class TotpEnableParams(TypedDict, total=False):
    code: str
    """TODO: Add more validations"""

    body_registration_id: Annotated[str, PropertyInfo(alias="registration_id")]
