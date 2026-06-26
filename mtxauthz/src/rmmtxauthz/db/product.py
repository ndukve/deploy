"""products that have been added to interop"""

from __future__ import annotations
from typing import Self
import logging
import functools

from sqlmodel import Field, select

from .base import ORMBaseModel
from .engine import EngineWrapper
from .errors import NotFound, Deleted
from .user import generate_code

LOGGER = logging.getLogger(__name__)


class Product(ORMBaseModel, table=True):
    """Products"""

    __tablename__ = "products"

    certcn: str = Field(index=True, unique=True, description="")
    mtxpassword: str = Field(
        description="Plaintext password we give to product for using MediaMTX",
        default_factory=generate_code,
    )
    stream_ro_password: str = Field(
        description="Plaintext password user can pass along for read/playback of any stream",
        default_factory=functools.partial(generate_code, 8, "RO_"),
    )

    @classmethod
    async def by_cn(cls, certcn: str, allow_deleted: bool = False) -> Self:
        """Get by certcn"""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.certcn == certcn)
            obj = session.exec(statement).first()
        if not obj:
            raise NotFound()
        if obj.deleted and not allow_deleted:
            raise Deleted()
        return obj
