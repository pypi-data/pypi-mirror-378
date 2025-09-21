# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ......_utils import PropertyInfo
from .organization_user_management_settings_param import OrganizationUserManagementSettingsParam

__all__ = ["UsermanagementPatchAllParams"]


class UsermanagementPatchAllParams(TypedDict, total=False):
    body_organization_id: Annotated[str, PropertyInfo(alias="organization_id")]

    settings: OrganizationUserManagementSettingsParam
