# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["EnvironmentDNSResponse", "DNSRecord"]


class DNSRecord(BaseModel):
    host_name: Optional[str] = None

    type: Optional[str] = None

    value: Optional[str] = None


class EnvironmentDNSResponse(BaseModel):
    dns_records: Optional[List[DNSRecord]] = None
