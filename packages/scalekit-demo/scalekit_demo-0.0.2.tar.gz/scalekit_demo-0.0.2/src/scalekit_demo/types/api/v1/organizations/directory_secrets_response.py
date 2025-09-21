# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .secret import Secret
from ....._models import BaseModel

__all__ = ["DirectorySecretsResponse"]


class DirectorySecretsResponse(BaseModel):
    plain_secret: Optional[str] = None

    secret: Optional[Secret] = None
