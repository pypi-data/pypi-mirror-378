# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["V1AuthSignupParams"]


class V1AuthSignupParams(TypedDict, total=False):
    first_name: str

    full_name: str

    last_name: str

    organization_name: str
    """making all optional for now"""

    phone_number: str
