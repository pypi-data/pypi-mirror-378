# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["EnvironmentSAMLCertificatesGenerateResponse"]


class EnvironmentSAMLCertificatesGenerateResponse(BaseModel):
    id: Optional[str] = None

    certificate: Optional[str] = None

    expiry: Optional[str] = None
