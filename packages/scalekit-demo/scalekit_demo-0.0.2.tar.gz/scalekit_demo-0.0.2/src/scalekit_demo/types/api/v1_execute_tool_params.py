# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["V1ExecuteToolParams"]


class V1ExecuteToolParams(TypedDict, total=False):
    connected_account_id: str

    connector: str

    identifier: str

    organization_id: str

    params: object

    tool_name: str

    user_id: str
