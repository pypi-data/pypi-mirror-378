# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ....._models import BaseModel

__all__ = ["Domain"]


class Domain(BaseModel):
    id: Optional[str] = None

    create_time: Optional[datetime] = None

    domain: Optional[str] = None

    domain_type: Optional[int] = None

    environment_id: Optional[str] = None

    organization_id: Optional[str] = None

    txt_record_key: Optional[str] = None

    txt_record_secret: Optional[str] = None

    update_time: Optional[datetime] = None

    verification_status: Optional[int] = None
