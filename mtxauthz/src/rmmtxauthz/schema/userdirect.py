"""Schemas for direct user mTLS routes"""

from pydantic import Field, BaseModel, ConfigDict


class UserCredentials(BaseModel):
    """Users credentials"""

    username: str = Field(description="MediaMTX username")
    password: str = Field(description="MediaMTX password")
    stream_ro_password: str = Field(
        description="Plaintext password user can pass along for read/playback of their streams",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "username": "KOIRA11a",
                    "password": "SomethingRandom",  # pragma: allowlist secret
                    "stream_ro_password": "SomethingRandom",  # pragma: allowlist secret
                },
            ],
        },
    )


class SRTPasswords(BaseModel):
    """SRT passwords"""

    publish: str = Field(description="Publish password")
    read: str = Field(description="Read password")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "publish": "SomethingElseRandom",  # pragma: allowlist secret
                    "read": "SomethingRandom",  # pragma: allowlist secret
                },
            ],
        },
    )
