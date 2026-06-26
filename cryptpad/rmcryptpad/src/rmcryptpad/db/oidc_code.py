"""OIDC authorization code persistence."""

from __future__ import annotations

import datetime
import hashlib
import secrets
from typing import Self

from sqlmodel import Field, select

from .base import ORMBaseModel
from .engine import EngineWrapper
from .errors import Deleted, NotFound


def hash_code(raw_code: str) -> str:
    """Hash a raw authorization code for storage."""
    return hashlib.sha256(raw_code.encode("utf-8")).hexdigest()


def _as_utc(dt: datetime.datetime) -> datetime.datetime:
    """Normalize datetimes so comparisons work with DB round-trips."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt.astimezone(datetime.UTC)


class OIDCAuthorizationCode(ORMBaseModel, table=True):
    """One-time OIDC authorization codes."""

    __tablename__ = "oidc_authorization_codes"

    code_hash: str = Field(index=True, unique=True)
    callsign: str = Field(index=True)
    client_id: str = Field(index=True)
    redirect_uri: str
    scope: str = "openid profile"
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    nonce: str | None = None
    expires_at: datetime.datetime = Field(index=True)
    used_at: datetime.datetime | None = Field(default=None, index=True)

    @classmethod
    async def issue(
        cls,
        *,
        callsign: str,
        client_id: str,
        redirect_uri: str,
        expires_at: datetime.datetime,
        code_challenge: str | None = None,
        code_challenge_method: str | None = None,
        nonce: str | None = None,
        scope: str = "openid profile",
    ) -> str:
        """Issue and persist a one-time authorization code."""
        raw_code = secrets.token_urlsafe(32)
        normalized_expires_at = _as_utc(expires_at)
        with EngineWrapper.get_session() as session:
            obj = cls(
                code_hash=hash_code(raw_code),
                callsign=callsign,
                client_id=client_id,
                redirect_uri=redirect_uri,
                expires_at=normalized_expires_at,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                nonce=nonce,
                scope=scope,
            )
            session.add(obj)
            session.commit()
        return raw_code

    @classmethod
    async def consume(cls, *, code: str, client_id: str, redirect_uri: str) -> Self:
        """Consume a one-time authorization code."""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(
                cls.code_hash == hash_code(code),
                cls.client_id == client_id,
                cls.redirect_uri == redirect_uri,
            )
            obj = session.exec(statement).first()
            if not obj:
                raise NotFound()
            expires_at = _as_utc(obj.expires_at)
            used_at = _as_utc(obj.used_at) if obj.used_at else None
            if (
                obj.deleted
                or used_at
                or expires_at <= datetime.datetime.now(datetime.UTC)
            ):
                raise Deleted()
            obj.used_at = datetime.datetime.now(datetime.UTC)
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj
