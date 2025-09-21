# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["PasswordLessConfig"]


class PasswordLessConfig(BaseModel):
    code_challenge_length: Optional[int] = None

    code_challenge_type: Optional[int] = None

    enforce_same_browser_origin: Optional[bool] = None

    frequency: Optional[int] = None

    regenerate_passwordless_credentials_on_resend: Optional[bool] = None

    type: Optional[int] = None

    validity: Optional[int] = None
