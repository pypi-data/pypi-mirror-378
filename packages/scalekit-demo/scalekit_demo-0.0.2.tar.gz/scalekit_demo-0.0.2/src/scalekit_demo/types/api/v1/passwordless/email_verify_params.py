# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..otp_request_param import OtpRequestParam

__all__ = ["EmailVerifyParams"]


class EmailVerifyParams(TypedDict, total=False):
    otp_req: OtpRequestParam
