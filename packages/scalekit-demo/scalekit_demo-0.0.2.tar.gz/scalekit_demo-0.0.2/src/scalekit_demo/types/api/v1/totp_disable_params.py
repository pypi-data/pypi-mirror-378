# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["TotpDisableParams"]


class TotpDisableParams(TypedDict, total=False):
    code: str

    body_registration_id: Annotated[str, PropertyInfo(alias="registration_id")]
