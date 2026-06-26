"""Product interoperability schemas."""

from typing import Optional

from pydantic import Field, BaseModel, ConfigDict


# FIXME: Move to libpvarki
class ProductAddRequest(BaseModel):
    """Request to add product interoperability."""

    certcn: str = Field(description="CN of the certificate")
    x509cert: str = Field(
        description="Certificate encoded with CFSSL conventions (newlines escaped)"
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "certcn": "product.deployment.tld",
                    "x509cert": "-----BEGIN CERTIFICATE-----\\nMIIEwjCC...\\n-----END CERTIFICATE-----\\n",
                },
            ],
        },
    )


# FIXME: Move to libpvarki
class ProductAuthzResponse(BaseModel):
    """Authz info"""

    type: str = Field(description="type of authz: bearer-token, basic, mtls")
    token: Optional[str] = Field(description="Bearer token", default=None)
    username: Optional[str] = Field(description="Username for basic auth", default=None)
    password: Optional[str] = Field(description="Password for basic auth", default=None)
    ro_password: Optional[str] = Field(
        description="Password for read-only streaming", default=None
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "type": "mtls",
                },
                {
                    "type": "bearer-token",
                    "token": "<JWT>",
                },
                {
                    "type": "basic",
                    "username": "product.deployment.tld",
                    "password": "<PASSWORD>",
                    "ro_password": "<PASSWORD>",
                },
            ],
        },
    )
