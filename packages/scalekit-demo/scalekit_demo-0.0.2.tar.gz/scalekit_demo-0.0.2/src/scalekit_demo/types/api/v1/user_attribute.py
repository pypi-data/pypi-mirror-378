# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["UserAttribute", "SSOAdditionInfo"]


class SSOAdditionInfo(BaseModel):
    default_oidc_mapping: Optional[str] = None

    default_saml_mapping: Optional[str] = None


class UserAttribute(BaseModel):
    category: Optional[int] = None

    datatype: Optional[int] = None

    directory_user_additional_info: Optional[object] = None

    enabled: Optional[bool] = None

    key: Optional[str] = None

    label: Optional[str] = None

    required: Optional[bool] = None

    sso_addition_info: Optional[SSOAdditionInfo] = None
