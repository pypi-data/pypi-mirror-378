# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["PasswordLessConfigParam"]


class PasswordLessConfigParam(TypedDict, total=False):
    code_challenge_length: int

    code_challenge_type: int

    enforce_same_browser_origin: bool

    frequency: int

    regenerate_passwordless_credentials_on_resend: bool

    type: int

    validity: int
