# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["AuthMethod"]


class AuthMethod(BaseModel):
    auth_initiation_uri: Optional[str] = None

    code_challenge_length: Optional[int] = None

    connection_id: Optional[str] = None

    connection_type: Optional[int] = None

    passwordless_type: Optional[int] = None

    provider: Optional[str] = None
