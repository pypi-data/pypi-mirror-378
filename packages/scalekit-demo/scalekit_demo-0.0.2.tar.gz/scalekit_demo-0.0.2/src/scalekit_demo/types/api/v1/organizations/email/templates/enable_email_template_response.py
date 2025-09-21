# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......._models import BaseModel

__all__ = ["EnableEmailTemplateResponse"]


class EnableEmailTemplateResponse(BaseModel):
    active_template_id: Optional[str] = None

    last_active_template_id: Optional[str] = None
