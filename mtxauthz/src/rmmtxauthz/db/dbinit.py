"""Ensure all models are defined and then create tables"""

import logging
from pathlib import Path
import tempfile
import asyncio
import random

import filelock
from sqlmodel import SQLModel
import sqlalchemy as sa
from sqlalchemy.schema import CreateSchema, DropSchema

from .engine import EngineWrapper

# Import all models to ensure ORM can create all tables
from .base import ORMBaseModel
from .user import User

_ = User
LOGGER = logging.getLogger(__name__)


async def init_db() -> None:
    """Create schemas and tables, normally one should use migration manager"""
    # Random sleep to avoid race conditions
    lockpath = Path(tempfile.gettempdir()) / "dbinit.lock"
    lock = filelock.FileLock(lockpath)
    wrapper = EngineWrapper.singleton()
    assert wrapper.engine  # nosec B101
    engine = wrapper.engine
    try:
        await asyncio.sleep(random.random() * 2)  # nosec
        lock.acquire(timeout=0.0)
        LOGGER.debug("Acquiring session")
        with engine.connect() as connection:
            if not sa.inspect(connection).has_schema(
                ORMBaseModel.__table_args__["schema"]
            ):
                LOGGER.debug(
                    "Creating schema {}".format(ORMBaseModel.__table_args__["schema"])
                )
                connection.execute(CreateSchema(ORMBaseModel.__table_args__["schema"]))
                connection.commit()
                LOGGER.debug("Creating tables")
                SQLModel.metadata.create_all(connection)
                connection.commit()
    except filelock.Timeout:
        LOGGER.warning("Someone has already locked {}".format(lockpath))
        LOGGER.debug("Sleeping for ~5s and then recursing")
        await asyncio.sleep(5.0 + random.random())  # nosec
        return await init_db()
    finally:
        lock.release()


async def drop_db() -> None:
    """Drop tables and schema"""
    wrapper = EngineWrapper.singleton()
    assert wrapper.engine  # nosec B101
    engine = wrapper.engine
    LOGGER.debug("Acquiring session")
    with engine.connect() as connection:
        LOGGER.debug("Dropping tables")
        SQLModel.metadata.drop_all(connection)
        connection.commit()
        LOGGER.debug("Dropping schema {}".format(ORMBaseModel.__table_args__["schema"]))
        connection.execute(DropSchema(ORMBaseModel.__table_args__["schema"]))
        connection.commit()
