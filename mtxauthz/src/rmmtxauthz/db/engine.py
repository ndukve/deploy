"""Engine stuff"""

from typing import ClassVar, Optional, Any
import logging
from dataclasses import dataclass, field

from sqlmodel import Session, create_engine

from ..config import DBSettings


LOGGER = logging.getLogger(__name__)


@dataclass
class EngineWrapper:
    """Handle engine singletons"""

    settings: DBSettings = field(default_factory=DBSettings.singleton)
    # FIXME: correct typing
    engine: Optional[Any] = field(default=None)

    _singleton: ClassVar[Optional["EngineWrapper"]] = None

    @classmethod
    def singleton(cls, **kwargs: Any) -> "EngineWrapper":
        """Get a singleton"""
        if EngineWrapper._singleton is None:
            EngineWrapper._singleton = EngineWrapper(**kwargs)
        assert EngineWrapper._singleton is not None  # nosec B101
        return EngineWrapper._singleton

    def __post_init__(self) -> None:
        """create one engine"""
        self.engine = create_engine(
            self.settings.dsn,
            pool_pre_ping=True,
            echo=self.settings.echo,
        )

    @classmethod
    def get_session(cls) -> Session:
        """Get a session from wrapper singleton"""
        return cls.singleton().session()

    def session(self) -> Session:
        """Get a session"""
        return Session(self.engine)
