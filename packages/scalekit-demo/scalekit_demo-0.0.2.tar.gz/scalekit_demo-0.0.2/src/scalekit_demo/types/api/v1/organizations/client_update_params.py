# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from ....._types import SequenceNotStr
from .custom_claim_param import CustomClaimParam

__all__ = ["ClientUpdateParams"]


class ClientUpdateParams(TypedDict, total=False):
    organization_id: Required[str]

    audience: SequenceNotStr[str]

    custom_claims: Iterable[CustomClaimParam]

    description: str

    expiry: str

    name: str

    scopes: SequenceNotStr[str]
