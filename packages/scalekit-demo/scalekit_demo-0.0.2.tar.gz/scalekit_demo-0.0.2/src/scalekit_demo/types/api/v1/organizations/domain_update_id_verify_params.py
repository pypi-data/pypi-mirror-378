# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DomainUpdateIDVerifyParams"]


class DomainUpdateIDVerifyParams(TypedDict, total=False):
    organization_id: Required[str]

    external_id: str
