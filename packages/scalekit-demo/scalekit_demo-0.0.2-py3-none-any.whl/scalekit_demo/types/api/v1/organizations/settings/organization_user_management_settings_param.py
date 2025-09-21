# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["OrganizationUserManagementSettingsParam"]


class OrganizationUserManagementSettingsParam(TypedDict, total=False):
    deprecated_placeholder: int
    """
    Deprecated placeholder to ensure google.protobuf.NullValue is referenced in the
    schema, preventing unused-definition warnings.
    """

    jit_provisioning_with_sso_enabled: bool

    sync_user_profile_on_signin: bool
