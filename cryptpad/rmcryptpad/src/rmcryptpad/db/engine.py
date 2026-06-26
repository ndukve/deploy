"""SQLModel engine helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional

from sqlmodel import Session, create_engine

from ..config import DBSettings


@dataclass
class EngineWrapper:
    """Manage the SQLModel engine singleton."""

    settings: DBSettings = field(default_factory=DBSettings.singleton)
    engine: Optional[Any] = field(default=None)

    _singleton: ClassVar[Optional["EngineWrapper"]] = None

    def __post_init__(self) -> None:
        self.engine = create_engine(
            self.settings.dsn, pool_pre_ping=True, echo=self.settings.echo
        )

    @classmethod
    def singleton(cls, **kwargs: Any) -> "EngineWrapper":
        """Return the singleton engine wrapper."""
        if cls._singleton is None:
            cls._singleton = cls(**kwargs)
        return cls._singleton

    @classmethod
    def get_session(cls) -> Session:
        """Return a database session."""
        return cls.singleton().session()

    def session(self) -> Session:
        """Return a session bound to the singleton engine."""
        return Session(self.engine)
