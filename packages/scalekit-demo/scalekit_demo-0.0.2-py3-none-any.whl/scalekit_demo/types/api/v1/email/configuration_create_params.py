# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ConfigurationCreateParams", "Server", "ServerSettings"]


class ConfigurationCreateParams(TypedDict, total=False):
    default_from_name: str

    server: Server


class ServerSettings(TypedDict, total=False):
    from_email: str

    from_name: str

    host: str

    password: str

    port: str

    username: str


class Server(TypedDict, total=False):
    id: str

    enabled: bool

    provider: int

    settings: ServerSettings
