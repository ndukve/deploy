"""Interop schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProductAddRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Interop product registration request."""

    model_config = ConfigDict(extra="forbid")

    certcn: str
    x509cert: str


class ProductAuthzResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Interop authz response."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["basic"] = "basic"
    username: str
    password: str
