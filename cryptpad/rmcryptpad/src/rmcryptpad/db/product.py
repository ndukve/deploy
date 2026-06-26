"""Interop product persistence."""

from __future__ import annotations

import secrets
import string
from typing import Self

from sqlmodel import Field, select

from .base import ORMBaseModel
from .engine import EngineWrapper
from .errors import Deleted, NotFound

PASSWORD_ALPHABET = string.ascii_letters + string.digits


def generate_secret(size: int = 32) -> str:
    """Generate a compact shared secret."""
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(size))


class Product(ORMBaseModel, table=True):
    """Interop credential state for peer products."""

    __tablename__ = "products"

    certcn: str = Field(index=True, unique=True)
    api_username: str = Field(index=True, unique=True)
    api_password: str = Field(default_factory=generate_secret)

    @classmethod
    async def by_cn(cls, certcn: str, allow_deleted: bool = False) -> Self:
        """Fetch a product by certificate CN."""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.certcn == certcn)
            obj = session.exec(statement).first()
        if not obj:
            raise NotFound()
        if obj.deleted and not allow_deleted:
            raise Deleted()
        return obj

    @classmethod
    async def create_or_update(cls, *, certcn: str) -> Self:
        """Create or re-enable a product interop row."""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.certcn == certcn)
            obj = session.exec(statement).first()
            if obj is None:
                obj = cls(certcn=certcn, api_username=certcn)
            else:
                obj.api_username = certcn
                obj.deleted = None
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj
