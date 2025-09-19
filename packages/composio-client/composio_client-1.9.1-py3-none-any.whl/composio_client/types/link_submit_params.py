# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["LinkSubmitParams"]


class LinkSubmitParams(TypedDict, total=False):
    input: Required[Dict[str, Optional[object]]]
    """The input fields for authentication"""
