# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .authorization_details_param import AuthorizationDetailsParam

__all__ = ["ConnectedAccountCreateParams", "ConnectedAccount"]


class ConnectedAccountCreateParams(TypedDict, total=False):
    connected_account: ConnectedAccount

    connector: str

    identifier: str

    organization_id: str

    user_id: str


class ConnectedAccount(TypedDict, total=False):
    api_config: object

    authorization_details: AuthorizationDetailsParam
