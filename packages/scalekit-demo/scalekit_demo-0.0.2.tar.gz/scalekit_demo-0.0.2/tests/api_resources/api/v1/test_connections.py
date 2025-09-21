# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    ConnectionListResponse,
    CreateConnectionResponse,
    ToggleConnectionResponse,
    UpdateConnectionResponse,
    ConnectionRetrieveResponse,
    ConnectionRetrieveAppResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConnections:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.create()
        assert_matches_type(CreateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.create(
            flags={
                "is_app": True,
                "is_login": True,
            },
            key_id="key_id",
            provider=0,
            provider_key="provider_key",
            type=0,
        )
        assert_matches_type(CreateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(CreateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(CreateConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.retrieve(
            test_request_id="test_request_id",
            connection_id="connection_id",
        )
        assert_matches_type(ConnectionRetrieveResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.retrieve(
            test_request_id="test_request_id",
            connection_id="connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ConnectionRetrieveResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.retrieve(
            test_request_id="test_request_id",
            connection_id="connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ConnectionRetrieveResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.api.v1.connections.with_raw_response.retrieve(
                test_request_id="test_request_id",
                connection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_request_id` but received ''"):
            client.api.v1.connections.with_raw_response.retrieve(
                test_request_id="",
                connection_id="connection_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.update(
            connection_id="connection_id",
        )
        assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.update(
            connection_id="connection_id",
            attribute_mapping={"foo": "string"},
            configuration_type=0,
            debug_enabled=True,
            key_id="key_id",
            oauth_config={
                "access_type": "access_type",
                "authorize_uri": "authorize_uri",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "custom_scope_name": "custom_scope_name",
                "pkce_enabled": True,
                "prompt": "prompt",
                "redirect_uri": "redirect_uri",
                "scopes": ["string"],
                "token_uri": "token_uri",
                "use_platform_creds": True,
                "user_info_uri": "user_info_uri",
            },
            oidc_config={
                "authorize_uri": "authorize_uri",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "discovery_endpoint": "discovery_endpoint",
                "idp_logout_required": True,
                "issuer": "issuer",
                "jwks_uri": "jwks_uri",
                "pkce_enabled": True,
                "redirect_uri": "redirect_uri",
                "scopes": [0],
                "token_auth_type": 0,
                "token_uri": "token_uri",
                "user_info_uri": "user_info_uri",
            },
            passwordless_config={
                "code_challenge_length": 0,
                "code_challenge_type": 0,
                "enforce_same_browser_origin": True,
                "frequency": 0,
                "regenerate_passwordless_credentials_on_resend": True,
                "type": 0,
                "validity": 0,
            },
            provider=0,
            provider_key="provider_key",
            saml_config={
                "assertion_encrypted": True,
                "certificate_id": "certificate_id",
                "default_redirect_uri": "default_redirect_uri",
                "force_authn": True,
                "idp_certificate": "idp_certificate",
                "idp_entity_id": "idp_entity_id",
                "idp_metadata_url": "idp_metadata_url",
                "idp_name_id_format": 0,
                "idp_slo_request_binding": 0,
                "idp_slo_required": True,
                "idp_slo_url": "idp_slo_url",
                "idp_sso_request_binding": 0,
                "idp_sso_url": "idp_sso_url",
                "saml_signing_option": 0,
                "sp_assertion_url": "sp_assertion_url",
                "sp_entity_id": "sp_entity_id",
                "sp_slo_url": "sp_slo_url",
                "ui_button_title": "ui_button_title",
                "want_request_signed": True,
            },
            static_config={"static_config": {}},
            type=0,
            ui_button_title="ui_button_title",
        )
        assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.update(
            connection_id="connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.update(
            connection_id="connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.api.v1.connections.with_raw_response.update(
                connection_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.list()
        assert_matches_type(ConnectionListResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.list(
            domain="domain",
            include="include",
            organization_id="organization_id",
        )
        assert_matches_type(ConnectionListResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ConnectionListResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ConnectionListResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.delete(
            "connection_id",
        )
        assert connection is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.delete(
            "connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert connection is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.delete(
            "connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert connection is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.api.v1.connections.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_app(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.retrieve_app()
        assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_app_with_all_params(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.retrieve_app(
            page_size=0,
            page_token="page_token",
            provider="provider",
        )
        assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_app(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.retrieve_app()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_app(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.retrieve_app() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_connection_id_disable(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.update_connection_id_disable(
            "connection_id",
        )
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_connection_id_disable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.update_connection_id_disable(
            "connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_connection_id_disable(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.update_connection_id_disable(
            "connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_connection_id_disable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.api.v1.connections.with_raw_response.update_connection_id_disable(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_connection_id_enable(self, client: ScalekitDemo) -> None:
        connection = client.api.v1.connections.update_connection_id_enable(
            "connection_id",
        )
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_connection_id_enable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.connections.with_raw_response.update_connection_id_enable(
            "connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = response.parse()
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_connection_id_enable(self, client: ScalekitDemo) -> None:
        with client.api.v1.connections.with_streaming_response.update_connection_id_enable(
            "connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = response.parse()
            assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_connection_id_enable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            client.api.v1.connections.with_raw_response.update_connection_id_enable(
                "",
            )


class TestAsyncConnections:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.create()
        assert_matches_type(CreateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.create(
            flags={
                "is_app": True,
                "is_login": True,
            },
            key_id="key_id",
            provider=0,
            provider_key="provider_key",
            type=0,
        )
        assert_matches_type(CreateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(CreateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(CreateConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.retrieve(
            test_request_id="test_request_id",
            connection_id="connection_id",
        )
        assert_matches_type(ConnectionRetrieveResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.retrieve(
            test_request_id="test_request_id",
            connection_id="connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ConnectionRetrieveResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.retrieve(
            test_request_id="test_request_id",
            connection_id="connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ConnectionRetrieveResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.api.v1.connections.with_raw_response.retrieve(
                test_request_id="test_request_id",
                connection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_request_id` but received ''"):
            await async_client.api.v1.connections.with_raw_response.retrieve(
                test_request_id="",
                connection_id="connection_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.update(
            connection_id="connection_id",
        )
        assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.update(
            connection_id="connection_id",
            attribute_mapping={"foo": "string"},
            configuration_type=0,
            debug_enabled=True,
            key_id="key_id",
            oauth_config={
                "access_type": "access_type",
                "authorize_uri": "authorize_uri",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "custom_scope_name": "custom_scope_name",
                "pkce_enabled": True,
                "prompt": "prompt",
                "redirect_uri": "redirect_uri",
                "scopes": ["string"],
                "token_uri": "token_uri",
                "use_platform_creds": True,
                "user_info_uri": "user_info_uri",
            },
            oidc_config={
                "authorize_uri": "authorize_uri",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "discovery_endpoint": "discovery_endpoint",
                "idp_logout_required": True,
                "issuer": "issuer",
                "jwks_uri": "jwks_uri",
                "pkce_enabled": True,
                "redirect_uri": "redirect_uri",
                "scopes": [0],
                "token_auth_type": 0,
                "token_uri": "token_uri",
                "user_info_uri": "user_info_uri",
            },
            passwordless_config={
                "code_challenge_length": 0,
                "code_challenge_type": 0,
                "enforce_same_browser_origin": True,
                "frequency": 0,
                "regenerate_passwordless_credentials_on_resend": True,
                "type": 0,
                "validity": 0,
            },
            provider=0,
            provider_key="provider_key",
            saml_config={
                "assertion_encrypted": True,
                "certificate_id": "certificate_id",
                "default_redirect_uri": "default_redirect_uri",
                "force_authn": True,
                "idp_certificate": "idp_certificate",
                "idp_entity_id": "idp_entity_id",
                "idp_metadata_url": "idp_metadata_url",
                "idp_name_id_format": 0,
                "idp_slo_request_binding": 0,
                "idp_slo_required": True,
                "idp_slo_url": "idp_slo_url",
                "idp_sso_request_binding": 0,
                "idp_sso_url": "idp_sso_url",
                "saml_signing_option": 0,
                "sp_assertion_url": "sp_assertion_url",
                "sp_entity_id": "sp_entity_id",
                "sp_slo_url": "sp_slo_url",
                "ui_button_title": "ui_button_title",
                "want_request_signed": True,
            },
            static_config={"static_config": {}},
            type=0,
            ui_button_title="ui_button_title",
        )
        assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.update(
            connection_id="connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.update(
            connection_id="connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(UpdateConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.api.v1.connections.with_raw_response.update(
                connection_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.list()
        assert_matches_type(ConnectionListResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.list(
            domain="domain",
            include="include",
            organization_id="organization_id",
        )
        assert_matches_type(ConnectionListResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ConnectionListResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ConnectionListResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.delete(
            "connection_id",
        )
        assert connection is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.delete(
            "connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert connection is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.delete(
            "connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert connection is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.api.v1.connections.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_app(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.retrieve_app()
        assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_app_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.retrieve_app(
            page_size=0,
            page_token="page_token",
            provider="provider",
        )
        assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_app(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.retrieve_app()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_app(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.retrieve_app() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ConnectionRetrieveAppResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_connection_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.update_connection_id_disable(
            "connection_id",
        )
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_connection_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.update_connection_id_disable(
            "connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_connection_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.update_connection_id_disable(
            "connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_connection_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.api.v1.connections.with_raw_response.update_connection_id_disable(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_connection_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        connection = await async_client.api.v1.connections.update_connection_id_enable(
            "connection_id",
        )
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_connection_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.connections.with_raw_response.update_connection_id_enable(
            "connection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection = await response.parse()
        assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_connection_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.connections.with_streaming_response.update_connection_id_enable(
            "connection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection = await response.parse()
            assert_matches_type(ToggleConnectionResponse, connection, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_connection_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `connection_id` but received ''"):
            await async_client.api.v1.connections.with_raw_response.update_connection_id_enable(
                "",
            )
