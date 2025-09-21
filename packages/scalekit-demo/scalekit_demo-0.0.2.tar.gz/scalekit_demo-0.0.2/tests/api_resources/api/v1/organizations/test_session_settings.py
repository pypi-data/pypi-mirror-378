# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1.organizations import (
    SessionSettingSessionSettingsResponse,
    SessionSettingUpdateSessionSettingsResponse,
    SessionSettingRetrieveSessionSettingsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessionSettings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_session_settings(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.delete_session_settings(
            id="id",
        )
        assert session_setting is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_session_settings_with_all_params(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.delete_session_settings(
            id="id",
            environment_id="environment_id",
        )
        assert session_setting is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_session_settings(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.session_settings.with_raw_response.delete_session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = response.parse()
        assert session_setting is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_session_settings(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.session_settings.with_streaming_response.delete_session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = response.parse()
            assert session_setting is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_session_settings(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.session_settings.with_raw_response.delete_session_settings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_session_settings(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.retrieve_session_settings(
            id="id",
        )
        assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_session_settings_with_all_params(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.retrieve_session_settings(
            id="id",
            environment_id="environment_id",
        )
        assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_session_settings(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.session_settings.with_raw_response.retrieve_session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = response.parse()
        assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_session_settings(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.session_settings.with_streaming_response.retrieve_session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = response.parse()
            assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_session_settings(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.session_settings.with_raw_response.retrieve_session_settings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_session_settings(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.session_settings(
            id="id",
        )
        assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_session_settings_with_all_params(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.session_settings(
            id="id",
            environment_id="environment_id",
        )
        assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_session_settings(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.session_settings.with_raw_response.session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = response.parse()
        assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_session_settings(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.session_settings.with_streaming_response.session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = response.parse()
            assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_session_settings(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.session_settings.with_raw_response.session_settings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_session_settings(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.update_session_settings(
            id="id",
        )
        assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_session_settings_with_all_params(self, client: ScalekitDemo) -> None:
        session_setting = client.api.v1.organizations.session_settings.update_session_settings(
            id="id",
            environment_id="environment_id",
            absolute_session_timeout=0,
            idle_session_enabled=True,
            idle_session_timeout=0,
            session_management_enabled=True,
        )
        assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_session_settings(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.session_settings.with_raw_response.update_session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = response.parse()
        assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_session_settings(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.session_settings.with_streaming_response.update_session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = response.parse()
            assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_session_settings(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.session_settings.with_raw_response.update_session_settings(
                id="",
            )


class TestAsyncSessionSettings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.delete_session_settings(
            id="id",
        )
        assert session_setting is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_session_settings_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.delete_session_settings(
            id="id",
            environment_id="environment_id",
        )
        assert session_setting is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.session_settings.with_raw_response.delete_session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = await response.parse()
        assert session_setting is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.session_settings.with_streaming_response.delete_session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = await response.parse()
            assert session_setting is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.session_settings.with_raw_response.delete_session_settings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.retrieve_session_settings(
            id="id",
        )
        assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_session_settings_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.retrieve_session_settings(
            id="id",
            environment_id="environment_id",
        )
        assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.session_settings.with_raw_response.retrieve_session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = await response.parse()
        assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.session_settings.with_streaming_response.retrieve_session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = await response.parse()
            assert_matches_type(SessionSettingRetrieveSessionSettingsResponse, session_setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.session_settings.with_raw_response.retrieve_session_settings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.session_settings(
            id="id",
        )
        assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_session_settings_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.session_settings(
            id="id",
            environment_id="environment_id",
        )
        assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.session_settings.with_raw_response.session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = await response.parse()
        assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.session_settings.with_streaming_response.session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = await response.parse()
            assert_matches_type(SessionSettingSessionSettingsResponse, session_setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.session_settings.with_raw_response.session_settings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.update_session_settings(
            id="id",
        )
        assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_session_settings_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        session_setting = await async_client.api.v1.organizations.session_settings.update_session_settings(
            id="id",
            environment_id="environment_id",
            absolute_session_timeout=0,
            idle_session_enabled=True,
            idle_session_timeout=0,
            session_management_enabled=True,
        )
        assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.session_settings.with_raw_response.update_session_settings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session_setting = await response.parse()
        assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.session_settings.with_streaming_response.update_session_settings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session_setting = await response.parse()
            assert_matches_type(SessionSettingUpdateSessionSettingsResponse, session_setting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_session_settings(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.session_settings.with_raw_response.update_session_settings(
                id="",
            )
