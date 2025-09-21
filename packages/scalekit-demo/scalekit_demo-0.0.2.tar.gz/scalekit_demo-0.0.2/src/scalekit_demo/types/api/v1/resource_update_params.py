# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["ResourceUpdateParams"]


class ResourceUpdateParams(TypedDict, total=False):
    update_mask: str

    access_token_expiry: str

    description: str

    disable_dynamic_client_registration: bool

    logo_uri: str

    name: str

    provider: str

    refresh_token_expiry: str

    body_resource_id: Annotated[str, PropertyInfo(alias="resource_id")]

    resource_uri: str

    scopes: SequenceNotStr[str]
