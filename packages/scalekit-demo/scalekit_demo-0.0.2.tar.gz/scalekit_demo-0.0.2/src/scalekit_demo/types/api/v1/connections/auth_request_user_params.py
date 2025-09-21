# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ....._types import SequenceNotStr

__all__ = ["AuthRequestUserParams"]


class AuthRequestUserParams(TypedDict, total=False):
    connection_id: Required[str]

    custom_attributes: object

    email: str

    email_verified: bool

    family_name: str

    gender: str

    given_name: str

    groups: SequenceNotStr[str]

    locale: str

    name: str

    phone_number: str

    phone_number_verified: bool

    picture: str

    preferred_username: str

    sub: str
