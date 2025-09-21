# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["EmailSendParams"]


class EmailSendParams(TypedDict, total=False):
    email: str

    expires_in: int

    magiclink_auth_uri: str

    state: str

    template: int

    template_variables: Dict[str, str]
