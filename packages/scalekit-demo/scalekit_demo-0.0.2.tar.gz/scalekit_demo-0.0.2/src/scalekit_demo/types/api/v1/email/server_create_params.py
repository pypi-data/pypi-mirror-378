# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .smtp_server_settings_param import SmtpServerSettingsParam

__all__ = ["ServerCreateParams"]


class ServerCreateParams(TypedDict, total=False):
    provider: int

    settings: SmtpServerSettingsParam
