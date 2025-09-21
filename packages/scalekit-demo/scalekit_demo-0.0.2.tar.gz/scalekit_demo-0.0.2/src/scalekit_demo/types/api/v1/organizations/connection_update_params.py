# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from ..static_auth_config_param import StaticAuthConfigParam
from ..password_less_config_param import PasswordLessConfigParam
from ..oidc_connection_config_param import OidcConnectionConfigParam
from ..oauth_connection_config_param import OAuthConnectionConfigParam

__all__ = ["ConnectionUpdateParams", "SAMLConfig"]


class ConnectionUpdateParams(TypedDict, total=False):
    organization_id: Required[str]

    attribute_mapping: Dict[str, str]

    configuration_type: int

    debug_enabled: bool

    key_id: str

    oauth_config: OAuthConnectionConfigParam

    oidc_config: OidcConnectionConfigParam

    passwordless_config: PasswordLessConfigParam

    provider: int

    provider_key: str

    saml_config: SAMLConfig

    static_config: StaticAuthConfigParam

    type: int

    ui_button_title: str


class SAMLConfig(TypedDict, total=False):
    assertion_encrypted: bool

    certificate_id: str

    default_redirect_uri: str

    force_authn: bool

    idp_certificate: str

    idp_entity_id: str

    idp_metadata_url: str

    idp_name_id_format: int

    idp_slo_request_binding: int

    idp_slo_required: bool

    idp_slo_url: str

    idp_sso_request_binding: int

    idp_sso_url: str

    saml_signing_option: int

    sp_assertion_url: str

    sp_entity_id: str

    sp_slo_url: str

    ui_button_title: str

    want_request_signed: bool
