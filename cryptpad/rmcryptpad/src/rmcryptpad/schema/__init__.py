"""Local request and response schemas for rmcryptpad."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from .clients import ClientDataPayload, ClientDataResponse
from .interop import ProductAddRequest, ProductAuthzResponse


class OperationResultResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Generic contract response."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    error: str | None = None


class UserCRUDRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Product user lifecycle request."""

    model_config = ConfigDict(extra="forbid")

    uuid: str
    callsign: str
    x509cert: str

    @field_validator("x509cert", mode="before")
    @classmethod
    def normalize_cfssl_pem(cls, value: str) -> str:
        """Accept the CFSSL-style escaped PEM used by the RM product contract."""
        if isinstance(value, str):
            return value.replace("\\r", "").replace("\\n", "\n")
        return value


class ProductDescription(BaseModel):  # pylint: disable=too-few-public-methods
    """Product description contract."""

    model_config = ConfigDict(extra="forbid")

    shortname: str
    title: str
    icon: str | None
    description: str
    language: str


class ProductComponent(BaseModel):  # pylint: disable=too-few-public-methods
    """Component metadata."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["link", "markdown", "component"]
    ref: str


class ProductDescriptionExtended(BaseModel):  # pylint: disable=too-few-public-methods
    """Extended product description contract."""

    model_config = ConfigDict(extra="forbid")

    shortname: str
    title: str
    icon: str | None
    description: str
    language: str
    docs: str
    component: ProductComponent


class InstructionsResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Instructions payload."""

    model_config = ConfigDict(extra="forbid")

    callsign: str
    instructions: str
    language: str


__all__ = [
    "ClientDataPayload",
    "ClientDataResponse",
    "InstructionsResponse",
    "OperationResultResponse",
    "ProductAddRequest",
    "ProductAuthzResponse",
    "ProductComponent",
    "ProductDescription",
    "ProductDescriptionExtended",
    "UserCRUDRequest",
]
