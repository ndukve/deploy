"""Schema and table initialization helpers."""

from __future__ import annotations

import asyncio
import random
import tempfile
from pathlib import Path

import filelock
import sqlalchemy as sa
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlmodel import SQLModel

from .base import ORMBaseModel
from .engine import EngineWrapper
from .oidc_code import OIDCAuthorizationCode
from .product import Product
from .user import User

_ = (OIDCAuthorizationCode, Product, User)


async def init_db() -> None:
    """Create the rmcryptpad schema and tables."""
    lockpath = Path(tempfile.gettempdir()) / "rmcryptpad-dbinit.lock"
    lock = filelock.FileLock(lockpath)
    wrapper = EngineWrapper.singleton()
    assert wrapper.engine is not None
    try:
        await asyncio.sleep(random.random() * 1.5)  # nosec
        lock.acquire(timeout=0.0)
        with wrapper.engine.connect() as connection:
            if not sa.inspect(connection).has_schema(
                ORMBaseModel.__table_args__["schema"]
            ):
                connection.execute(CreateSchema(ORMBaseModel.__table_args__["schema"]))
                connection.commit()
            SQLModel.metadata.create_all(connection)
            connection.commit()
    except filelock.Timeout:
        await asyncio.sleep(1.0 + random.random())  # nosec
        await init_db()
    finally:
        if lock.is_locked:
            lock.release()


async def drop_db() -> None:
    """Drop all rmcryptpad tables and schema."""
    wrapper = EngineWrapper.singleton()
    assert wrapper.engine is not None
    with wrapper.engine.connect() as connection:
        if sa.inspect(connection).has_schema(ORMBaseModel.__table_args__["schema"]):
            SQLModel.metadata.drop_all(connection)
            connection.commit()
            connection.execute(DropSchema(ORMBaseModel.__table_args__["schema"]))
            connection.commit()
