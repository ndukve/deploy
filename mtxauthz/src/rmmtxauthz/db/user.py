"""Users"""

from __future__ import annotations
from typing import AsyncGenerator, Self
import logging
import uuid
import secrets
import string
import functools


from sqlmodel import Field, select

from .base import ORMBaseModel
from .engine import EngineWrapper
from .errors import NotFound, Deleted

LOGGER = logging.getLogger(__name__)

CODE_ALPHABET = string.ascii_uppercase + string.digits


def generate_code(size: int = 12, prefix: str = "") -> str:
    """Generate a code"""
    code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(size))
    code = code.replace("0", "O").replace("1", "I")
    return f"{prefix}{code}"


class User(ORMBaseModel, table=True):
    """Users"""

    __tablename__ = "users"

    rmuuid: uuid.UUID = Field(
        index=True, unique=True, description="RASENMAEHER user UUID"
    )
    username: str = Field(index=True, unique=True, description="Unique username")
    mtxpassword: str = Field(
        description="Plaintext password we give to user for using MediaMTX",
        default_factory=generate_code,
    )
    stream_ro_password: str = Field(
        description="Plaintext password user can pass along for read/playback of their streams",
        default_factory=functools.partial(generate_code, 8, "RO_"),
    )
    is_rmadmin: bool = Field(
        default=False, description="User has admin role in RASENMAEHER"
    )

    @classmethod
    async def by_username(cls, username: str, allow_deleted: bool = False) -> Self:
        """Get by username"""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.username == username)
            obj = session.exec(statement).first()
        if not obj:
            raise NotFound()
        if obj.deleted and not allow_deleted:
            raise Deleted()
        return obj

    @classmethod
    async def by_rmuuid(
        cls, rmuuid: str | uuid.UUID, allow_deleted: bool = False
    ) -> Self:
        """Get by username"""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.rmuuid == rmuuid)
            obj = session.exec(statement).first()
        if not obj:
            raise NotFound()
        if obj.deleted and not allow_deleted:
            raise Deleted()
        return obj

    @classmethod
    async def list(
        cls,
        include_deleted: bool = False,
    ) -> AsyncGenerator["User", None]:
        """List users, optionally including deleted users"""
        with EngineWrapper.get_session() as session:
            statement = select(cls)
            if not include_deleted:
                statement = statement.where(
                    cls.deleted == None  # noqa: E711 ; # "is None" will create invalid query
                )
            results = session.exec(statement)
            for result in results:
                result.mtxpassword = "REDACTED"  # nosec  # pragma: allowlist secret
                yield result
