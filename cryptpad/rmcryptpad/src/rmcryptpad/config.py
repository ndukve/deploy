"""Application settings."""

from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import util
from sqlalchemy.engine.url import URL


class DBSettings(BaseSettings):
    """Database configuration for rmcryptpad."""

    driver: str = "postgresql+psycopg2"
    host: str = "localhost"
    port: int = 5432
    user: str = "rmcryptpad"
    password: str = "rmcryptpad"  # pragma: allowlist secret
    database: str = "rmcryptpad"
    echo: bool = False

    model_config = SettingsConfigDict(env_prefix="RMCRYPTPAD_DATABASE_", extra="ignore")

    _singleton: ClassVar[Optional["DBSettings"]] = None

    @property
    def dsn(self) -> URL:
        """Return the database DSN."""
        return URL(
            drivername=self.driver,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query=util.EMPTY_DICT,
        )

    @classmethod
    def singleton(cls) -> "DBSettings":
        """Return the cached DB settings instance."""
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton


class RMCryptPadSettings(BaseSettings):
    """Runtime settings for rmcryptpad."""

    rmcn: str = Field(
        default="rasenmaeher",
        description="Expected CN for the Rasenmaeher client certificate",
    )
    public_url: str = "https://cryptpad.localhost:8443"
    public_sandbox_url: str = "https://sandbox.cryptpad.localhost:8443"
    docs_url: str = "https://docs.cryptpad.org/en/admin_guide/installation.html"
    ui_dir: str = "/opt/ui/cryptpad"
    oidc_issuer: str = "https://rmcryptpad.localhost:8443"
    oidc_key_dir: str = "/data/oidc"
    oidc_client_id: str = "cryptpad"
    oidc_client_secret: str = "cryptpad-secret"
    oidc_code_ttl_seconds: int = 300
    oidc_token_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(env_prefix="RMCRYPTPAD_", extra="ignore")

    _singleton: ClassVar[Optional["RMCryptPadSettings"]] = None

    @classmethod
    def singleton(cls) -> "RMCryptPadSettings":
        """Return a cached settings instance."""
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton
