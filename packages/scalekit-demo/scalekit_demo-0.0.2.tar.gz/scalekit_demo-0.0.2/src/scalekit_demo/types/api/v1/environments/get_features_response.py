# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ....._models import BaseModel
from .environment_feature import EnvironmentFeature

__all__ = ["GetFeaturesResponse"]


class GetFeaturesResponse(BaseModel):
    features: Optional[List[EnvironmentFeature]] = None
