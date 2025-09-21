# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from ...._models import BaseModel
from .static_auth_config import StaticAuthConfig
from .organizations.domain import Domain
from .password_less_config import PasswordLessConfig
from .oidc_connection_config import OidcConnectionConfig
from .oauth_connection_config import OAuthConnectionConfig

__all__ = ["Connection", "SAMLConfig", "SAMLConfigIdpCertificate"]


class SAMLConfigIdpCertificate(BaseModel):
    id: Optional[str] = None

    certificate: Optional[str] = None

    create_time: Optional[datetime] = None

    expiry_time: Optional[datetime] = None

    issuer: Optional[str] = None


class SAMLConfig(BaseModel):
    allow_idp_initiated_login: Optional[bool] = None

    assertion_encrypted: Optional[bool] = None

    certificate_id: Optional[str] = None

    default_redirect_uri: Optional[str] = None

    force_authn: Optional[bool] = None

    idp_certificates: Optional[List[SAMLConfigIdpCertificate]] = None

    idp_entity_id: Optional[str] = None

    idp_metadata_url: Optional[str] = None

    idp_name_id_format: Optional[int] = None

    idp_slo_request_binding: Optional[int] = None

    idp_slo_required: Optional[bool] = None

    idp_slo_url: Optional[str] = None

    idp_sso_request_binding: Optional[int] = None

    idp_sso_url: Optional[str] = None

    saml_signing_option: Optional[int] = None

    sp_assertion_url: Optional[str] = None

    sp_entity_id: Optional[str] = None

    sp_metadata_url: Optional[str] = None

    sp_slo_url: Optional[str] = None

    ui_button_title: Optional[str] = None

    want_request_signed: Optional[bool] = None


class Connection(BaseModel):
    id: Optional[str] = None

    attribute_mapping: Optional[Dict[str, str]] = None

    configuration_type: Optional[int] = None

    create_time: Optional[datetime] = None

    debug_enabled: Optional[bool] = None

    domains: Optional[List[Domain]] = None

    enabled: Optional[bool] = None

    key_id: Optional[str] = None

    oauth_config: Optional[OAuthConnectionConfig] = None

    oidc_config: Optional[OidcConnectionConfig] = None

    organization_id: Optional[str] = None

    passwordless_config: Optional[PasswordLessConfig] = None

    provider: Optional[int] = None

    provider_key: Optional[str] = None

    saml_config: Optional[SAMLConfig] = None

    static_config: Optional[StaticAuthConfig] = None

    status: Optional[int] = None

    test_connection_uri: Optional[str] = None

    type: Optional[int] = None

    ui_button_title: Optional[str] = None

    update_time: Optional[datetime] = None
