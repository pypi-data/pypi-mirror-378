# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["ConnectionRetrieveResponse"]


class ConnectionRetrieveResponse(BaseModel):
    error: Optional[str] = None

    error_description: Optional[str] = None

    error_details: Optional[str] = None

    status: Optional[int] = None

    user_info: Optional[str] = None
