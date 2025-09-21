# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .member import Member
from ...._models import BaseModel

__all__ = ["MemberCreateResponse"]


class MemberCreateResponse(BaseModel):
    member: Optional[Member] = None
