# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["ResourceClientsRegisterParams"]


class ResourceClientsRegisterParams(TypedDict, total=False):
    client_name: str

    client_uri: str

    description: str

    logo_uri: str

    policy_uri: str

    redirect_uris: SequenceNotStr[str]

    scope: str

    tos_uri: str
