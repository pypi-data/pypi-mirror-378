# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["SSOUserAttributeUpdateParams", "SSOAdditionInfo"]


class SSOUserAttributeUpdateParams(TypedDict, total=False):
    datatype: int

    directory_user_additional_info: object

    enabled: bool

    body_key: Annotated[str, PropertyInfo(alias="key")]

    label: str

    required: bool

    sso_addition_info: SSOAdditionInfo


class SSOAdditionInfo(TypedDict, total=False):
    default_oidc_mapping: str

    default_saml_mapping: str
