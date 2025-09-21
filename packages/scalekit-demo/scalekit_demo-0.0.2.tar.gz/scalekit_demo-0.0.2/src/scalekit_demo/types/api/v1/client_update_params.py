# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["ClientUpdateParams"]


class ClientUpdateParams(TypedDict, total=False):
    mask: str

    back_channel_logout_uris: SequenceNotStr[str]

    default_redirect_uri: str

    initiate_login_uri: str

    post_login_uris: SequenceNotStr[str]

    post_logout_redirect_uris: SequenceNotStr[str]

    redirect_uris: SequenceNotStr[str]
