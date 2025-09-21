# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    EnvironmentDNSResponse,
    GetEnvironmentResponse,
    EnvironmentListResponse,
    EnvironmentAssetResponse,
    EnvironmentCreateResponse,
    UpdateEnvironmentResponse,
    EnvironmentCustomDomainsResponse,
    UpdatePortalCustomizationResponse,
    EnvironmentSAMLCertificatesGenerateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEnvironments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.create()
        assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.create(
            display_name="display_name",
            region_code=0,
            type=0,
        )
        assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.retrieve(
            "id",
        )
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.update(
            id="id",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.update(
            id="id",
            display_name="display_name",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.list()
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.list(
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentListResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.delete(
            "id",
        )
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert environment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_asset(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.asset(
            id="id",
        )
        assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_asset_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.asset(
            id="id",
            category=0,
            extension="extension",
        )
        assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_asset(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.asset(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_asset(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.asset(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_asset(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.with_raw_response.asset(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_custom_domains(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.custom_domains(
            path_id="id",
        )
        assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_custom_domains_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.custom_domains(
            path_id="id",
            body_id="id",
            custom_domain="custom_domain",
        )
        assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_custom_domains(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.custom_domains(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_custom_domains(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.custom_domains(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_custom_domains(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.environments.with_raw_response.custom_domains(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_custom_domains_check(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.custom_domains_check(
            path_id="id",
        )
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_custom_domains_check_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.custom_domains_check(
            path_id="id",
            body_id="id",
        )
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_custom_domains_check(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.custom_domains_check(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_custom_domains_check(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.custom_domains_check(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_custom_domains_check(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.environments.with_raw_response.custom_domains_check(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dns(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.dns(
            path_id="id",
        )
        assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dns_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.dns(
            path_id="id",
            body_id="id",
            custom_domain="custom_domain",
        )
        assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_dns(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.dns(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_dns(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.dns(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_dns(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.environments.with_raw_response.dns(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dns_verify(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.dns_verify(
            path_id="id",
        )
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dns_verify_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.dns_verify(
            path_id="id",
            body_id="id",
            custom_domain="custom_domain",
        )
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_dns_verify(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.dns_verify(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_dns_verify(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.dns_verify(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert environment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_dns_verify(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.environments.with_raw_response.dns_verify(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_saml_certificates_generate(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.saml_certificates_generate(
            path_id="id",
        )
        assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_saml_certificates_generate_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.saml_certificates_generate(
            path_id="id",
            body_id="id",
        )
        assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_saml_certificates_generate(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.saml_certificates_generate(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_saml_certificates_generate(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.saml_certificates_generate(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_saml_certificates_generate(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.environments.with_raw_response.saml_certificates_generate(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_customizations(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.update_customizations(
            id="id",
            body={},
        )
        assert_matches_type(UpdatePortalCustomizationResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_customizations(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.update_customizations(
            id="id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(UpdatePortalCustomizationResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_customizations(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.update_customizations(
            id="id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(UpdatePortalCustomizationResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_customizations(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.with_raw_response.update_customizations(
                id="",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_id_update(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.update_id_update(
            id="id",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_id_update_with_all_params(self, client: ScalekitDemo) -> None:
        environment = client.api.v1.environments.update_id_update(
            id="id",
            domain="domain",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_id_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.environments.with_raw_response.update_id_update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_id_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.environments.with_streaming_response.update_id_update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_id_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.environments.with_raw_response.update_id_update(
                id="",
            )


class TestAsyncEnvironments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.create()
        assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.create(
            display_name="display_name",
            region_code=0,
            type=0,
        )
        assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentCreateResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.retrieve(
            "id",
        )
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.update(
            id="id",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.update(
            id="id",
            display_name="display_name",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.list()
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.list(
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentListResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.delete(
            "id",
        )
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert environment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_asset(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.asset(
            id="id",
        )
        assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_asset_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.asset(
            id="id",
            category=0,
            extension="extension",
        )
        assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_asset(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.asset(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_asset(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.asset(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentAssetResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_asset(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.asset(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_custom_domains(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.custom_domains(
            path_id="id",
        )
        assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_custom_domains_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.custom_domains(
            path_id="id",
            body_id="id",
            custom_domain="custom_domain",
        )
        assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_custom_domains(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.custom_domains(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_custom_domains(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.custom_domains(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentCustomDomainsResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_custom_domains(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.custom_domains(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_custom_domains_check(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.custom_domains_check(
            path_id="id",
        )
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_custom_domains_check_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.custom_domains_check(
            path_id="id",
            body_id="id",
        )
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_custom_domains_check(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.custom_domains_check(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_custom_domains_check(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.custom_domains_check(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(GetEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_custom_domains_check(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.custom_domains_check(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dns(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.dns(
            path_id="id",
        )
        assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dns_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.dns(
            path_id="id",
            body_id="id",
            custom_domain="custom_domain",
        )
        assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_dns(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.dns(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_dns(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.dns(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentDNSResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_dns(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.dns(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dns_verify(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.dns_verify(
            path_id="id",
        )
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dns_verify_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.dns_verify(
            path_id="id",
            body_id="id",
            custom_domain="custom_domain",
        )
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_dns_verify(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.dns_verify(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert environment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_dns_verify(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.dns_verify(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert environment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_dns_verify(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.dns_verify(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_saml_certificates_generate(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.saml_certificates_generate(
            path_id="id",
        )
        assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_saml_certificates_generate_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.saml_certificates_generate(
            path_id="id",
            body_id="id",
        )
        assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_saml_certificates_generate(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.saml_certificates_generate(
            path_id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_saml_certificates_generate(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.saml_certificates_generate(
            path_id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentSAMLCertificatesGenerateResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_saml_certificates_generate(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.saml_certificates_generate(
                path_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_customizations(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.update_customizations(
            id="id",
            body={},
        )
        assert_matches_type(UpdatePortalCustomizationResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_customizations(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.update_customizations(
            id="id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(UpdatePortalCustomizationResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_customizations(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.update_customizations(
            id="id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(UpdatePortalCustomizationResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_customizations(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.update_customizations(
                id="",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_id_update(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.update_id_update(
            id="id",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_id_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        environment = await async_client.api.v1.environments.update_id_update(
            id="id",
            domain="domain",
        )
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_id_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.environments.with_raw_response.update_id_update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_id_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.environments.with_streaming_response.update_id_update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(UpdateEnvironmentResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_id_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.environments.with_raw_response.update_id_update(
                id="",
            )
