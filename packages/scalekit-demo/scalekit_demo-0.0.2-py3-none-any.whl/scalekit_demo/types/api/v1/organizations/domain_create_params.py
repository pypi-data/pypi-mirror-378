# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DomainCreateParams"]


class DomainCreateParams(TypedDict, total=False):
    connection_id: str

    external_id: str

    domain: str

    domain_type: int
