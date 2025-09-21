# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ......_models import BaseModel

__all__ = ["OrganizationUserManagementSettings"]


class OrganizationUserManagementSettings(BaseModel):
    deprecated_placeholder: Optional[int] = None
    """
    Deprecated placeholder to ensure google.protobuf.NullValue is referenced in the
    schema, preventing unused-definition warnings.
    """

    jit_provisioning_with_sso_enabled: Optional[bool] = None

    sync_user_profile_on_signin: Optional[bool] = None
