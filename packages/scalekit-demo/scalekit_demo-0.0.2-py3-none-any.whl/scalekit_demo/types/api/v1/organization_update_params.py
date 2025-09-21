# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["OrganizationUpdateParams"]


class OrganizationUpdateParams(TypedDict, total=False):
    query_external_id: Annotated[str, PropertyInfo(alias="external_id")]

    update_mask: str

    display_name: str

    body_external_id: Annotated[str, PropertyInfo(alias="external_id")]

    metadata: Dict[str, str]
