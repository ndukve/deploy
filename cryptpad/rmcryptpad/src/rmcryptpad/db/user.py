"""User persistence for rmcryptpad."""

from __future__ import annotations

import datetime
from typing import AsyncGenerator, Self

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from sqlmodel import Field, select

from .base import ORMBaseModel
from .engine import EngineWrapper
from .errors import Deleted, NotFound


def fingerprint_pem(cert_pem: str) -> str:
    """Generate a stable fingerprint for a stored certificate PEM."""
    certificate = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
    return certificate.fingerprint(
        hashes.SHA1()  # nosec B303 - x509 fingerprint convention
    ).hex()


class User(ORMBaseModel, table=True):
    """Rasenmaeher user state keyed by callsign."""

    __tablename__ = "users"

    callsign: str = Field(
        index=True, unique=True, description="Canonical CryptPad identity"
    )
    rmuuid: str = Field(
        index=True, description="Latest RM UUID observed for this callsign"
    )
    cert_pem: str = Field(description="Current client certificate PEM")
    cert_fingerprint: str = Field(
        index=True, description="SHA-256 fingerprint of cert_pem"
    )
    is_rmadmin: bool = Field(default=False)
    revoked: datetime.datetime | None = Field(default=None, index=True)

    @classmethod
    async def by_callsign(cls, callsign: str, allow_inactive: bool = False) -> Self:
        """Fetch a user by callsign."""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.callsign == callsign)
            obj = session.exec(statement).first()
        if not obj:
            raise NotFound()
        if (obj.deleted or obj.revoked) and not allow_inactive:
            raise Deleted()
        return obj

    @classmethod
    async def create_or_update(
        cls,
        *,
        callsign: str,
        rmuuid: str,
        cert_pem: str,
        is_rmadmin: bool | None = None,
    ) -> Self:
        """Upsert a user using callsign as the stable identity key."""
        cert_hash = fingerprint_pem(cert_pem)
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.callsign == callsign)
            obj = session.exec(statement).first()
            if obj is None:
                obj = cls(
                    callsign=callsign,
                    rmuuid=rmuuid,
                    cert_pem=cert_pem,
                    cert_fingerprint=cert_hash,
                    is_rmadmin=is_rmadmin if is_rmadmin is not None else False,
                )
            else:
                obj.rmuuid = rmuuid
                obj.cert_pem = cert_pem
                obj.cert_fingerprint = cert_hash
                if is_rmadmin is not None:
                    obj.is_rmadmin = is_rmadmin
                obj.revoked = None
                obj.deleted = None
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj

    @classmethod
    async def list(cls, include_inactive: bool = False) -> AsyncGenerator["User", None]:
        """List users, excluding revoked/deleted records by default."""
        with EngineWrapper.get_session() as session:
            statement = select(cls)
            if not include_inactive:
                statement = statement.where(
                    cls.deleted == None,  # pylint: disable=singleton-comparison
                    cls.revoked == None,  # pylint: disable=singleton-comparison
                )
            for result in session.exec(statement):
                yield result
