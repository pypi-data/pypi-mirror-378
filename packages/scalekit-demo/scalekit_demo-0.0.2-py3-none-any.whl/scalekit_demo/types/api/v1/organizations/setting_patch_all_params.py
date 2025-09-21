# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

__all__ = ["SettingPatchAllParams", "Feature"]


class SettingPatchAllParams(TypedDict, total=False):
    features: Iterable[Feature]


class Feature(TypedDict, total=False):
    enabled: bool

    name: str
