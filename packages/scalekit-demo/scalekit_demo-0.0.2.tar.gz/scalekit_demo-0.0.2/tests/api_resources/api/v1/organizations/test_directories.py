# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from scalekit_demo import ScalekitDemo, AsyncScalekitDemo
from scalekit_demo._utils import parse_datetime
from scalekit_demo.types.api.v1.organizations import (
    DirectoryListResponse,
    DirectoryCreateResponse,
    DirectoryUpdateResponse,
    ToggleDirectoryResponse,
    DirectorySecretsResponse,
    DirectoryRetrieveResponse,
    DirectoryRetrieveUsersResponse,
    DirectoryUpdateAttributesResponse,
    DirectorySecretsRegenerateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDirectories:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.create(
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.create(
            organization_id="organization_id",
            directory_provider=0,
            directory_type=0,
        )
        assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.create(
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.create(
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.create(
                organization_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.retrieve(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryRetrieveResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.retrieve(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectoryRetrieveResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.retrieve(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectoryRetrieveResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.retrieve(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.retrieve(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update(
            id="id",
            organization_id="organization_id",
            directory_provider=0,
            directory_type=0,
            enabled=True,
            groups=[
                {
                    "display_name": "display_name",
                    "email": "email",
                    "external_id": "external_id",
                }
            ],
            mappings=[
                {
                    "display_name": "display_name",
                    "key": "key",
                    "map_to": "map_to",
                }
            ],
            name="name",
            status=0,
        )
        assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.update(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.update(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.list(
            "organization_id",
        )
        assert_matches_type(DirectoryListResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.list(
            "organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectoryListResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.list(
            "organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectoryListResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.delete(
            id="id",
            organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.delete(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.delete(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert directory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.delete(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.delete(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_directory_id_sync(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.retrieve_directory_id_sync(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_directory_id_sync(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.retrieve_directory_id_sync(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_directory_id_sync(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.retrieve_directory_id_sync(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert directory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_directory_id_sync(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.retrieve_directory_id_sync(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.retrieve_directory_id_sync(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_users(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_users_with_all_params(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
            directory_group_id="directory_group_id",
            include_detail=True,
            page_size=0,
            page_token="page_token",
            updated_after=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_users(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_users(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_users(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.retrieve_users(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.retrieve_users(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_secrets(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.secrets(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectorySecretsResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_secrets(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.secrets(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectorySecretsResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_secrets(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.secrets(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectorySecretsResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_secrets(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.secrets(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.secrets(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_secrets_regenerate(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.secrets_regenerate(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectorySecretsRegenerateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_secrets_regenerate(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.secrets_regenerate(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectorySecretsRegenerateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_secrets_regenerate(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.secrets_regenerate(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectorySecretsRegenerateResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_secrets_regenerate(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.secrets_regenerate(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.secrets_regenerate(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_attributes(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update_attributes(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_attributes_with_all_params(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update_attributes(
            id="id",
            organization_id="organization_id",
            attributes=[
                {
                    "key": "key",
                    "map_to": "map_to",
                }
            ],
        )
        assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_attributes(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.update_attributes(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_attributes(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.update_attributes(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_attributes(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_attributes(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_attributes(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_groups_assign(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_groups_assign_with_all_params(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
            body_id="id",
            external_ids=["string"],
            body_organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_groups_assign(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_groups_assign(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert directory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_groups_assign(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_groups_assign(
                path_id="id",
                path_organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_groups_assign(
                path_id="",
                path_organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_id_disable(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update_id_disable(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_id_disable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.update_id_disable(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_id_disable(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.update_id_disable(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_id_disable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_id_disable(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_id_disable(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_id_enable(self, client: ScalekitDemo) -> None:
        directory = client.api.v1.organizations.directories.update_id_enable(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_id_enable(self, client: ScalekitDemo) -> None:
        response = client.api.v1.organizations.directories.with_raw_response.update_id_enable(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = response.parse()
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_id_enable(self, client: ScalekitDemo) -> None:
        with client.api.v1.organizations.directories.with_streaming_response.update_id_enable(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = response.parse()
            assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_id_enable(self, client: ScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_id_enable(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.api.v1.organizations.directories.with_raw_response.update_id_enable(
                id="",
                organization_id="organization_id",
            )


class TestAsyncDirectories:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.create(
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.create(
            organization_id="organization_id",
            directory_provider=0,
            directory_type=0,
        )
        assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.create(
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.create(
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectoryCreateResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.create(
                organization_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.retrieve(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryRetrieveResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.retrieve(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectoryRetrieveResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.retrieve(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectoryRetrieveResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.retrieve(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.retrieve(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update(
            id="id",
            organization_id="organization_id",
            directory_provider=0,
            directory_type=0,
            enabled=True,
            groups=[
                {
                    "display_name": "display_name",
                    "email": "email",
                    "external_id": "external_id",
                }
            ],
            mappings=[
                {
                    "display_name": "display_name",
                    "key": "key",
                    "map_to": "map_to",
                }
            ],
            name="name",
            status=0,
        )
        assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.update(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.update(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectoryUpdateResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.list(
            "organization_id",
        )
        assert_matches_type(DirectoryListResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.list(
            "organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectoryListResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.list(
            "organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectoryListResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.delete(
            id="id",
            organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.delete(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.delete(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert directory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.delete(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.delete(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_directory_id_sync(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.retrieve_directory_id_sync(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_directory_id_sync(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.retrieve_directory_id_sync(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_directory_id_sync(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.retrieve_directory_id_sync(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert directory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_directory_id_sync(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.retrieve_directory_id_sync(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.retrieve_directory_id_sync(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_users(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_users_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
            directory_group_id="directory_group_id",
            include_detail=True,
            page_size=0,
            page_token="page_token",
            updated_after=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_users(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_users(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.retrieve_users(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectoryRetrieveUsersResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_users(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.retrieve_users(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.retrieve_users(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_secrets(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.secrets(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectorySecretsResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_secrets(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.secrets(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectorySecretsResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_secrets(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.secrets(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectorySecretsResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_secrets(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.secrets(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.secrets(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_secrets_regenerate(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.secrets_regenerate(
            directory_id="directory_id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectorySecretsRegenerateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_secrets_regenerate(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.secrets_regenerate(
            directory_id="directory_id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectorySecretsRegenerateResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_secrets_regenerate(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.secrets_regenerate(
            directory_id="directory_id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectorySecretsRegenerateResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_secrets_regenerate(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.secrets_regenerate(
                directory_id="directory_id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `directory_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.secrets_regenerate(
                directory_id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_attributes(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update_attributes(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_attributes_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update_attributes(
            id="id",
            organization_id="organization_id",
            attributes=[
                {
                    "key": "key",
                    "map_to": "map_to",
                }
            ],
        )
        assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_attributes(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.update_attributes(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_attributes(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.update_attributes(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(DirectoryUpdateAttributesResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_attributes(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_attributes(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_attributes(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_groups_assign(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_groups_assign_with_all_params(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
            body_id="id",
            external_ids=["string"],
            body_organization_id="organization_id",
        )
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_groups_assign(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert directory is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_groups_assign(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.update_groups_assign(
            path_id="id",
            path_organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert directory is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_groups_assign(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_groups_assign(
                path_id="id",
                path_organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_groups_assign(
                path_id="",
                path_organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update_id_disable(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.update_id_disable(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.update_id_disable(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_id_disable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_id_disable(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_id_disable(
                id="",
                organization_id="organization_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        directory = await async_client.api.v1.organizations.directories.update_id_enable(
            id="id",
            organization_id="organization_id",
        )
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        response = await async_client.api.v1.organizations.directories.with_raw_response.update_id_enable(
            id="id",
            organization_id="organization_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        directory = await response.parse()
        assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        async with async_client.api.v1.organizations.directories.with_streaming_response.update_id_enable(
            id="id",
            organization_id="organization_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            directory = await response.parse()
            assert_matches_type(ToggleDirectoryResponse, directory, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_id_enable(self, async_client: AsyncScalekitDemo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_id_enable(
                id="id",
                organization_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.api.v1.organizations.directories.with_raw_response.update_id_enable(
                id="",
                organization_id="organization_id",
            )
