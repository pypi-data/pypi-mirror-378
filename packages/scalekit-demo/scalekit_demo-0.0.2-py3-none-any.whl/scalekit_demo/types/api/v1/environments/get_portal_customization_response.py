# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["GetPortalCustomizationResponse"]


class GetPortalCustomizationResponse(BaseModel):
    customization_settings: Optional[object] = None

    environment_id: Optional[str] = FieldInfo(alias="environmentId", default=None)
