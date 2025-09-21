# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SmtpServerSettingsParam"]


class SmtpServerSettingsParam(TypedDict, total=False):
    from_email: str

    from_name: str

    host: str

    password: str

    port: str

    username: str
