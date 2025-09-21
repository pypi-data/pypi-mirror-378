# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .template import Template
from ......_models import BaseModel

__all__ = ["ListEmailTemplateResponse"]


class ListEmailTemplateResponse(BaseModel):
    templates: Optional[List[Template]] = None
