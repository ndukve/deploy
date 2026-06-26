"""Client data schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ClientDataPayload(BaseModel):  # pylint: disable=too-few-public-methods
    """Client data payload."""

    model_config = ConfigDict(extra="forbid")

    url: str
    sandbox_url: str
    docs_url: str
    oidc_issuer: str


class ClientDataResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Nested client data response."""

    model_config = ConfigDict(extra="forbid")

    data: ClientDataPayload
