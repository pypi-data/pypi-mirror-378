# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["WebhookUpdateResponse"]


class WebhookUpdateResponse(BaseModel):
    event_payload: Optional[object] = None

    event_type: Optional[str] = None
