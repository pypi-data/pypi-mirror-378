# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["EnvironmentAssetResponse"]


class EnvironmentAssetResponse(BaseModel):
    fetch_url: Optional[str] = None

    upload_url: Optional[str] = None
