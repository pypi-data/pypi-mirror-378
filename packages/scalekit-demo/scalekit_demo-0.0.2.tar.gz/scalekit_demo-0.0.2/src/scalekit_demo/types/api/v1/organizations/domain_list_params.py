# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DomainListParams"]


class DomainListParams(TypedDict, total=False):
    connection_id: str

    domain_type: int

    external_id: str

    include: str

    page_number: int

    page_size: int
