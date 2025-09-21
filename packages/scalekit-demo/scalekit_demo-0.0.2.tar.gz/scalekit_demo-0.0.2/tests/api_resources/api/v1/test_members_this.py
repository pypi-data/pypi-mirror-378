# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo.types.api.v1 import (
    GetMemberResponse,
    UpdateMemberResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMembersThis:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_members_this(self, client: ScalekitDemo) -> None:
        members_this = client.api.v1.members_this.retrieve_members_this()
        assert_matches_type(GetMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_members_this(self, client: ScalekitDemo) -> None:
        response = client.api.v1.members_this.with_raw_response.retrieve_members_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        members_this = response.parse()
        assert_matches_type(GetMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_members_this(self, client: ScalekitDemo) -> None:
        with client.api.v1.members_this.with_streaming_response.retrieve_members_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            members_this = response.parse()
            assert_matches_type(GetMemberResponse, members_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_members_this(self, client: ScalekitDemo) -> None:
        members_this = client.api.v1.members_this.update_members_this()
        assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_members_this_with_all_params(self, client: ScalekitDemo) -> None:
        members_this = client.api.v1.members_this.update_members_this(
            first_name="first_name",
            last_name="last_name",
            metadata={"foo": "string"},
            role=0,
            user_profile={
                "custom_attributes": {"foo": "string"},
                "first_name": "first_name",
                "last_name": "last_name",
                "locale": "locale",
                "metadata": {"foo": "string"},
                "name": "name",
                "phone_number": "phone_number",
            },
        )
        assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_members_this(self, client: ScalekitDemo) -> None:
        response = client.api.v1.members_this.with_raw_response.update_members_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        members_this = response.parse()
        assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_members_this(self, client: ScalekitDemo) -> None:
        with client.api.v1.members_this.with_streaming_response.update_members_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            members_this = response.parse()
            assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMembersThis:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_members_this(self, async_client: AsyncScalekitDemo) -> None:
        members_this = await async_client.api.v1.members_this.retrieve_members_this()
        assert_matches_type(GetMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_members_this(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.members_this.with_raw_response.retrieve_members_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        members_this = await response.parse()
        assert_matches_type(GetMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_members_this(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.members_this.with_streaming_response.retrieve_members_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            members_this = await response.parse()
            assert_matches_type(GetMemberResponse, members_this, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_members_this(self, async_client: AsyncScalekitDemo) -> None:
        members_this = await async_client.api.v1.members_this.update_members_this()
        assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_members_this_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        members_this = await async_client.api.v1.members_this.update_members_this(
            first_name="first_name",
            last_name="last_name",
            metadata={"foo": "string"},
            role=0,
            user_profile={
                "custom_attributes": {"foo": "string"},
                "first_name": "first_name",
                "last_name": "last_name",
                "locale": "locale",
                "metadata": {"foo": "string"},
                "name": "name",
                "phone_number": "phone_number",
            },
        )
        assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_members_this(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.members_this.with_raw_response.update_members_this()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        members_this = await response.parse()
        assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_members_this(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.members_this.with_streaming_response.update_members_this() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            members_this = await response.parse()
            assert_matches_type(UpdateMemberResponse, members_this, path=["response"])

        assert cast(Any, response.is_closed) is True
