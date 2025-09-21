# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api import (
    V1SignupResponse,
    V1RetrieveResponse,
    V1FetchBulkResponse,
    V1AuthSignupResponse,
    V1ExecuteToolResponse,
    V1AuthDiscoveryResponse,
    V1ToolsSetDefaultResponse,
    V1RetrieveAuthmethodsResponse,
    V1RetrieveUsersSearchResponse,
    V1RetrieveAuthFeaturesResponse,
    V1RetrieveAuthOrganizationsResponse,
    V1RetrieveAuthCustomizationsResponse,
    V1RetrieveOrganizationsSearchResponse,
    V1RetrieveConnectedAccountsSearchResponse,
)
from scalekit_demo.types.api.v1 import UpdateDefaultRolesResponse
from scalekit_demo.types.api.v1.environments import GetCurrentSessionResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestV1:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve(
            "origin",
        )
        assert_matches_type(V1RetrieveResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve(
            "origin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve(
            "origin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `origin` but received ''"):
            client.api.v1.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_auth_discovery(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.auth_discovery()
        assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_auth_discovery_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.auth_discovery(
            email="email",
            intent=0,
        )
        assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_auth_discovery(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.auth_discovery()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_auth_discovery(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.auth_discovery() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_auth_signup(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.auth_signup()
        assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_auth_signup_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.auth_signup(
            first_name="first_name",
            full_name="full_name",
            last_name="last_name",
            organization_name="organization_name",
            phone_number="phone_number",
        )
        assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_auth_signup(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.auth_signup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_auth_signup(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.auth_signup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connected_accounts_delete(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.connected_accounts_delete()
        assert_matches_type(object, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connected_accounts_delete_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.connected_accounts_delete(
            id="id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(object, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_connected_accounts_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.connected_accounts_delete()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(object, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_connected_accounts_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.connected_accounts_delete() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(object, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_tool(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.execute_tool()
        assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_tool_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.execute_tool(
            connected_account_id="connected_account_id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            params={},
            tool_name="tool_name",
            user_id="user_id",
        )
        assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_tool(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.execute_tool()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_tool(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.execute_tool() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_bulk(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.fetch_bulk()
        assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_bulk_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.fetch_bulk(
            resources=[
                {
                    "identifiers": ["string"],
                    "type": 0,
                }
            ],
        )
        assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_fetch_bulk(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.fetch_bulk()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_fetch_bulk(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.fetch_bulk() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_auth_customizations(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_auth_customizations()
        assert_matches_type(V1RetrieveAuthCustomizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_auth_customizations(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_auth_customizations()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveAuthCustomizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_auth_customizations(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_auth_customizations() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveAuthCustomizationsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_auth_features(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_auth_features()
        assert_matches_type(V1RetrieveAuthFeaturesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_auth_features(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_auth_features()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveAuthFeaturesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_auth_features(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_auth_features() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveAuthFeaturesResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_auth_organizations(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_auth_organizations()
        assert_matches_type(V1RetrieveAuthOrganizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_auth_organizations(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_auth_organizations()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveAuthOrganizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_auth_organizations(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_auth_organizations() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveAuthOrganizationsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_authmethods(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_authmethods()
        assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_authmethods_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_authmethods(
            intent="intent",
        )
        assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_authmethods(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_authmethods()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_authmethods(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_authmethods() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_connected_accounts_search(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_connected_accounts_search()
        assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_connected_accounts_search_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_connected_accounts_search(
            connection_id="connection_id",
            page_size=0,
            page_token="page_token",
            query="query",
        )
        assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_connected_accounts_search(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_connected_accounts_search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_connected_accounts_search(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_connected_accounts_search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_organizations_search(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_organizations_search()
        assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_organizations_search_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_organizations_search(
            page_size=0,
            page_token="page_token",
            query="query",
        )
        assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_organizations_search(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_organizations_search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_organizations_search(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_organizations_search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_session_active(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_session_active()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_session_active(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_session_active()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_session_active(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_session_active() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert v1 is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_sessions_me()
        assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_sessions_me_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_sessions_me(
            id="id",
        )
        assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_sessions_me()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_sessions_me(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_sessions_me() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_users_search(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_users_search()
        assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_users_search_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.retrieve_users_search(
            page_size=0,
            page_token="page_token",
            query="query",
        )
        assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_users_search(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.retrieve_users_search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_users_search(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.retrieve_users_search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_signup(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.signup()
        assert_matches_type(V1SignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_signup_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.signup(
            company="company",
            email="email",
        )
        assert_matches_type(V1SignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_signup(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.signup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1SignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_signup(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.signup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1SignupResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tools_set_default(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.tools_set_default()
        assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tools_set_default_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.tools_set_default(
            name="name",
            schema_version="schema_version",
            tool_version="tool_version",
        )
        assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_tools_set_default(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.tools_set_default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_tools_set_default(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.tools_set_default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_roles_set_defaults(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.update_roles_set_defaults()
        assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_roles_set_defaults_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.update_roles_set_defaults(
            default_creator={
                "id": "id",
                "name": "name",
            },
            default_creator_role="default_creator_role",
            default_member={
                "id": "id",
                "name": "name",
            },
            default_member_role="default_member_role",
        )
        assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_roles_set_defaults(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.update_roles_set_defaults()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_roles_set_defaults(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.update_roles_set_defaults() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_workspaces_onboard(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.update_workspaces_onboard()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_workspaces_onboard_with_all_params(self, client: ScalekitDemo) -> None:
        v1 = client.api.v1.update_workspaces_onboard(
            user_family_name="user_family_name",
            user_given_name="user_given_name",
            workspace_display_name="workspace_display_name",
        )
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_workspaces_onboard(self, client: ScalekitDemo) -> None:
        response = client.api.v1.with_raw_response.update_workspaces_onboard()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_workspaces_onboard(self, client: ScalekitDemo) -> None:
        with client.api.v1.with_streaming_response.update_workspaces_onboard() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert v1 is None

        assert cast(Any, response.is_closed) is True


class TestAsyncV1:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve(
            "origin",
        )
        assert_matches_type(V1RetrieveResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve(
            "origin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve(
            "origin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `origin` but received ''"):
            await async_client.api.v1.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_auth_discovery(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.auth_discovery()
        assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_auth_discovery_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.auth_discovery(
            email="email",
            intent=0,
        )
        assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_auth_discovery(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.auth_discovery()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_auth_discovery(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.auth_discovery() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1AuthDiscoveryResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_auth_signup(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.auth_signup()
        assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_auth_signup_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.auth_signup(
            first_name="first_name",
            full_name="full_name",
            last_name="last_name",
            organization_name="organization_name",
            phone_number="phone_number",
        )
        assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_auth_signup(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.auth_signup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_auth_signup(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.auth_signup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1AuthSignupResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connected_accounts_delete(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.connected_accounts_delete()
        assert_matches_type(object, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connected_accounts_delete_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.connected_accounts_delete(
            id="id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            user_id="user_id",
        )
        assert_matches_type(object, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_connected_accounts_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.connected_accounts_delete()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(object, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_connected_accounts_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.connected_accounts_delete() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(object, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_tool(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.execute_tool()
        assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_tool_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.execute_tool(
            connected_account_id="connected_account_id",
            connector="connector",
            identifier="identifier",
            organization_id="organization_id",
            params={},
            tool_name="tool_name",
            user_id="user_id",
        )
        assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_tool(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.execute_tool()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_tool(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.execute_tool() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1ExecuteToolResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_bulk(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.fetch_bulk()
        assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_bulk_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.fetch_bulk(
            resources=[
                {
                    "identifiers": ["string"],
                    "type": 0,
                }
            ],
        )
        assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_fetch_bulk(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.fetch_bulk()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_fetch_bulk(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.fetch_bulk() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1FetchBulkResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_auth_customizations(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_auth_customizations()
        assert_matches_type(V1RetrieveAuthCustomizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_auth_customizations(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_auth_customizations()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveAuthCustomizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_auth_customizations(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_auth_customizations() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveAuthCustomizationsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_auth_features(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_auth_features()
        assert_matches_type(V1RetrieveAuthFeaturesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_auth_features(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_auth_features()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveAuthFeaturesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_auth_features(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_auth_features() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveAuthFeaturesResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_auth_organizations(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_auth_organizations()
        assert_matches_type(V1RetrieveAuthOrganizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_auth_organizations(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_auth_organizations()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveAuthOrganizationsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_auth_organizations(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_auth_organizations() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveAuthOrganizationsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_authmethods(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_authmethods()
        assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_authmethods_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_authmethods(
            intent="intent",
        )
        assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_authmethods(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_authmethods()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_authmethods(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_authmethods() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveAuthmethodsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_connected_accounts_search(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_connected_accounts_search()
        assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_connected_accounts_search_with_all_params(
        self, async_client: AsyncScalekitDemo
    ) -> None:
        v1 = await async_client.api.v1.retrieve_connected_accounts_search(
            connection_id="connection_id",
            page_size=0,
            page_token="page_token",
            query="query",
        )
        assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_connected_accounts_search(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_connected_accounts_search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_connected_accounts_search(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_connected_accounts_search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveConnectedAccountsSearchResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_organizations_search(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_organizations_search()
        assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_organizations_search_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_organizations_search(
            page_size=0,
            page_token="page_token",
            query="query",
        )
        assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_organizations_search(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_organizations_search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_organizations_search(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_organizations_search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveOrganizationsSearchResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_session_active(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_session_active()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_session_active(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_session_active()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_session_active(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_session_active() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert v1 is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_sessions_me()
        assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_sessions_me_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_sessions_me(
            id="id",
        )
        assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_sessions_me()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_sessions_me(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_sessions_me() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(GetCurrentSessionResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_users_search(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_users_search()
        assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_users_search_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.retrieve_users_search(
            page_size=0,
            page_token="page_token",
            query="query",
        )
        assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_users_search(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.retrieve_users_search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_users_search(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.retrieve_users_search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1RetrieveUsersSearchResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_signup(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.signup()
        assert_matches_type(V1SignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_signup_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.signup(
            company="company",
            email="email",
        )
        assert_matches_type(V1SignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_signup(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.signup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1SignupResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_signup(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.signup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1SignupResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tools_set_default(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.tools_set_default()
        assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tools_set_default_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.tools_set_default(
            name="name",
            schema_version="schema_version",
            tool_version="tool_version",
        )
        assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_tools_set_default(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.tools_set_default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_tools_set_default(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.tools_set_default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1ToolsSetDefaultResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_roles_set_defaults(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.update_roles_set_defaults()
        assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_roles_set_defaults_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.update_roles_set_defaults(
            default_creator={
                "id": "id",
                "name": "name",
            },
            default_creator_role="default_creator_role",
            default_member={
                "id": "id",
                "name": "name",
            },
            default_member_role="default_member_role",
        )
        assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_roles_set_defaults(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.update_roles_set_defaults()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_roles_set_defaults(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.update_roles_set_defaults() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(UpdateDefaultRolesResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_workspaces_onboard(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.update_workspaces_onboard()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_workspaces_onboard_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        v1 = await async_client.api.v1.update_workspaces_onboard(
            user_family_name="user_family_name",
            user_given_name="user_given_name",
            workspace_display_name="workspace_display_name",
        )
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_workspaces_onboard(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.with_raw_response.update_workspaces_onboard()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert v1 is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_workspaces_onboard(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.with_streaming_response.update_workspaces_onboard() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert v1 is None

        assert cast(Any, response.is_closed) is True
