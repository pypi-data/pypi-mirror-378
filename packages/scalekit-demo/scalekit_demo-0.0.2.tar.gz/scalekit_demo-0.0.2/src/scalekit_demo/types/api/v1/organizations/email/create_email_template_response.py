# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .template import Template
from ......_models import BaseModel

__all__ = ["CreateEmailTemplateResponse"]


class CreateEmailTemplateResponse(BaseModel):
    template: Optional[Template] = None
