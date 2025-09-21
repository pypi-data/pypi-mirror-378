# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scalekit_demo import ScalekitDemo, AsyncScalekitDemo

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDisable:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_template_id_disable(self, client: ScalekitDemo) -> None:
        disable = client.api.v1.organizations.email.templates.disable.update_template_id_disable(
            template_id="template_id",
            organization_id="organization_id",
        )
        assert disable is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_template_id_disable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.email.templates.disable.with_raw_response.update_template_id_disable(
            template_id="template_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disable = response.parse()
        assert disable is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_template_id_disable(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.email.templates.disable.with_streaming_response.update_template_id_disable(
            template_id="template_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disable = response.parse()
            assert disable is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_template_id_disable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.email.templates.disable.with_raw_response.update_template_id_disable(
                template_id="template_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `template_id` but received ''"):
            client.api.v1.organizations.email.templates.disable.with_raw_response.update_template_id_disable(
                template_id="",
                organization_id="organization_id",
            )


class TestAsyncDisable:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_template_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        disable = await async_client.api.v1.organizations.email.templates.disable.update_template_id_disable(
            template_id="template_id",
            organization_id="organization_id",
        )
        assert disable is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_template_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.email.templates.disable.with_raw_response.update_template_id_disable(
            template_id="template_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disable = await response.parse()
        assert disable is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_template_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.email.templates.disable.with_streaming_response.update_template_id_disable(
            template_id="template_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disable = await response.parse()
            assert disable is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_template_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await (
                async_client.api.v1.organizations.email.templates.disable.with_raw_response.update_template_id_disable(
                    template_id="template_id",
                    organization_id="",
                )
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `template_id` but received ''"):
            await (
                async_client.api.v1.organizations.email.templates.disable.with_raw_response.update_template_id_disable(
                    template_id="",
                    organization_id="organization_id",
                )
            )
