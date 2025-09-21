# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel

__all__ = ["User"]


class User(BaseModel):
    custom_attributes: Optional[object] = None

    email: Optional[str] = None

    email_verified: Optional[bool] = None

    family_name: Optional[str] = None

    gender: Optional[str] = None

    given_name: Optional[str] = None

    groups: Optional[List[str]] = None

    locale: Optional[str] = None

    name: Optional[str] = None

    phone_number: Optional[str] = None

    phone_number_verified: Optional[bool] = None

    picture: Optional[str] = None

    preferred_username: Optional[str] = None

    sub: Optional[str] = None
