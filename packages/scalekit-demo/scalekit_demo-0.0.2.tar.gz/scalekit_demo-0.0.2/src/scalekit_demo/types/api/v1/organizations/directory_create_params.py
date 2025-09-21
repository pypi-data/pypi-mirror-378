# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DirectoryCreateParams"]


class DirectoryCreateParams(TypedDict, total=False):
    directory_provider: int

    directory_type: int
