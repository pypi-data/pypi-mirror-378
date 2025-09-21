# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["V1UpdateWorkspacesOnboardParams"]


class V1UpdateWorkspacesOnboardParams(TypedDict, total=False):
    user_family_name: str

    user_given_name: str

    workspace_display_name: str
