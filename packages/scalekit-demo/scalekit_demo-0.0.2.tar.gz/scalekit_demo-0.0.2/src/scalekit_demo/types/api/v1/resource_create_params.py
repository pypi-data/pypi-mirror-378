# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["ResourceCreateParams"]


class ResourceCreateParams(TypedDict, total=False):
    access_token_expiry: str

    description: str

    disable_dynamic_client_registration: bool

    logo_uri: str

    name: str

    provider: str

    refresh_token_expiry: str

    resource_id: str

    resource_type: int

    resource_uri: str

    scopes: SequenceNotStr[str]
