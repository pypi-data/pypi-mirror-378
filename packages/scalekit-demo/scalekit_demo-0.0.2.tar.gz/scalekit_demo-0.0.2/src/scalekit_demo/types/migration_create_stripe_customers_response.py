# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["MigrationCreateStripeCustomersResponse"]


class MigrationCreateStripeCustomersResponse(BaseModel):
    error_messages: Optional[List[str]] = None

    failed_workspaces: Optional[int] = None

    success_workspaces: Optional[int] = None
