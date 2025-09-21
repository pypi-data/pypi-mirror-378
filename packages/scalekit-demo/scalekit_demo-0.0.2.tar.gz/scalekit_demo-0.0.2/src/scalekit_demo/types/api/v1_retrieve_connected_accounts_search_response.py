# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .v1.connected_account_for_list import ConnectedAccountForList

__all__ = ["V1RetrieveConnectedAccountsSearchResponse"]


class V1RetrieveConnectedAccountsSearchResponse(BaseModel):
    connected_accounts: Optional[List[ConnectedAccountForList]] = None

    next_page_token: Optional[str] = None

    prev_page_token: Optional[str] = None

    total_size: Optional[int] = None
