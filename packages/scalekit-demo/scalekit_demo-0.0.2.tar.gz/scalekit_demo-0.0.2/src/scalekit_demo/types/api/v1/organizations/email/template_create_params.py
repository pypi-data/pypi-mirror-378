# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TemplateCreateParams"]


class TemplateCreateParams(TypedDict, total=False):
    html_content: str

    plain_content: str

    subject: str

    use_case: int
