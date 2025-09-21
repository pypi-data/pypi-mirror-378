# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["MigrationCreateFsaDataParams"]


class MigrationCreateFsaDataParams(TypedDict, total=False):
    batch_size: int

    data_type: int

    environment_ids: SequenceNotStr[str]
