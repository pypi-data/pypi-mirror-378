# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ......_models import BaseModel

__all__ = ["Template"]


class Template(BaseModel):
    id: Optional[str] = None

    enabled: Optional[bool] = None

    html_content: Optional[str] = None

    placeholders: Optional[List[str]] = None

    plain_content: Optional[str] = None

    subject: Optional[str] = None

    updated_at: Optional[datetime] = None

    use_case: Optional[int] = None
