# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["MagicLinkCreateParams"]


class MagicLinkCreateParams(TypedDict, total=False):
    id: str

    connector: str

    identifier: str

    organization_id: str

    user_id: str
