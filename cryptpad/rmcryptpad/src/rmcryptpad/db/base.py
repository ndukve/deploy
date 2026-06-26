"""Shared ORM primitives."""

from __future__ import annotations

import datetime
import uuid
from typing import Self

import sqlalchemy as sa
from sqlmodel import Field, SQLModel, select

from .engine import EngineWrapper
from .errors import Deleted, NotFound

utcnow = sa.func.current_timestamp()  # pylint: disable=invalid-name,not-callable


class ORMBaseModel(SQLModel, table=False):
    """Common ORM fields for rmcryptpad models."""

    __table_args__ = {"schema": "rmcryptpad"}

    pk: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    created: datetime.datetime = Field(
        sa_column_kwargs={"default": utcnow}, nullable=False
    )
    updated: datetime.datetime = Field(
        sa_column_kwargs={"default": utcnow, "onupdate": utcnow}, nullable=False
    )
    deleted: datetime.datetime | None = Field(default=None, nullable=True)

    @classmethod
    async def by_pk(cls, pkin: uuid.UUID, allow_deleted: bool = False) -> Self:
        """Fetch an object by primary key."""
        with EngineWrapper.get_session() as session:
            statement = select(cls).where(cls.pk == pkin)
            obj = session.exec(statement).first()
        if not obj:
            raise NotFound()
        if obj.deleted and not allow_deleted:
            raise Deleted()
        return obj

    async def soft_delete(self) -> Self:
        """Mark an object deleted without removing it."""
        with EngineWrapper.get_session() as session:
            self.deleted = datetime.datetime.now(datetime.UTC)
            session.add(self)
            session.commit()
            session.refresh(self)
        return self
