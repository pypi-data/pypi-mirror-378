# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["ToggleConnectionResponse"]


class ToggleConnectionResponse(BaseModel):
    enabled: Optional[bool] = None

    error_message: Optional[str] = None
