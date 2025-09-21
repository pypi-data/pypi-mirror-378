# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel
from ..organizations.email.template import Template

__all__ = ["TemplateRetrieveUsecasesResponse", "UseCase", "UseCasePlaceholder"]


class UseCasePlaceholder(BaseModel):
    category: Optional[str] = None

    category_priority: Optional[int] = None

    description: Optional[str] = None

    display: Optional[bool] = None

    name: Optional[str] = None

    title: Optional[str] = None


class UseCase(BaseModel):
    default_template: Optional[Template] = None

    description: Optional[str] = None

    display: Optional[bool] = None

    placeholders: Optional[List[UseCasePlaceholder]] = None

    title: Optional[str] = None

    use_case: Optional[int] = None


class TemplateRetrieveUsecasesResponse(BaseModel):
    use_cases: Optional[List[UseCase]] = None
