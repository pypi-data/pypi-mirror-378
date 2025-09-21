# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel
from .client_secret import ClientSecret

__all__ = ["SecretCreateResponse"]


class SecretCreateResponse(BaseModel):
    plain_secret: Optional[str] = None

    secret: Optional[ClientSecret] = None
