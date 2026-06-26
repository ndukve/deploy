"""Configurations"""

from typing import ClassVar, Optional, Annotated, NamedTuple, Dict, Sequence
import logging
from functools import cached_property

from pydantic import Field
from pydantic.types import StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL
from sqlalchemy import util

LOGGER = logging.getLogger(__name__)
UCStr = Annotated[str, StringConstraints(to_upper=True)]


class Protocol(NamedTuple):
    """URL protocol and port"""

    proto: str
    port: int


class DBSettings(BaseSettings):
    """Database settings"""

    driver: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    user: str = "rmmtx"
    password: str = "<PASSWORD>"  # pragma: allowlist secret
    database: str = "rmmtx"
    echo: bool = False

    model_config = SettingsConfigDict(env_prefix="RMMTX_DATABASE_", extra="ignore")

    _singleton: ClassVar[Optional["DBSettings"]] = None

    @property
    def dsn(self) -> URL:
        """Return the DSN URL for the db"""
        return URL(
            drivername=self.driver,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query=util.EMPTY_DICT,
        )

    @classmethod
    def singleton(cls) -> "DBSettings":
        """Return singleton"""
        if not DBSettings._singleton:
            DBSettings._singleton = DBSettings()
        return DBSettings._singleton


class RMMTXSettings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8005
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = True
    log_level: UCStr = Field(default="INFO", alias="LOG_LEVEL")
    rmcn: str = Field(
        default="rasenmaeher", description="expected CN for RASENMAEHERs mTLS cert"
    )

    api_username: str = Field(
        default="rmmtxauthz", description="Username for *this* integration to use"
    )
    api_password: str = Field(
        default="CHANGEME", description="Password for *this* integration to use"
    )
    api_url: str = Field(
        default="https://mediamtx:9997", description="URL for the MediaMTX control API"
    )
    srt_pub_password: str = Field(
        default="CHANGEME", description="SRT Password for *this* integration to use"
    )
    srt_read_password: str = Field(
        default="CHANGEME", description="SRT Password for *this* integration to use"
    )

    mtx_address: str = Field(
        default="__REQUEST_HOSTNAME__", description="Public address for MediaMTX server"
    )
    mtx_hls_port: int = Field(default=9888, description="HLS stream port")
    mtx_webrtc_port: int = Field(default=9889, description="WebRTC stream port")
    mtx_rtsps_port: int = Field(default=8322, description="RTSPs stream port")
    mtx_rtmps_port: int = Field(default=1936, description="RTMPs stream port")
    mtx_srt_port: int = Field(default=8890, description="SRT stream port")
    mtx_protocols: str = Field(
        default="hls,webrtc,rtsps,rtmps,srt",
        description="Which protocols to generate URLs for",
    )

    user_path_prefixes: str = Field(
        default="live",
        description="Valid path prefixes for users (path format PREFIX/TOOL/CALLSIGN)",
    )
    user_path_tools: str = Field(
        default="icu,gopro,uas,ipcam",
        description="Valid tool components for users (path format PREFIX/TOOL/CALLSIGN)",
    )

    model_config = SettingsConfigDict(env_prefix="RMMTX_", extra="ignore")

    _singleton: ClassVar[Optional["RMMTXSettings"]] = None

    @classmethod
    def singleton(cls) -> "RMMTXSettings":
        """Return singleton"""
        if not RMMTXSettings._singleton:
            RMMTXSettings._singleton = RMMTXSettings()
        return RMMTXSettings._singleton

    @cached_property
    def prefixes(self) -> Sequence[str]:
        """Return user_path_prefixes as list"""
        return [prefix.strip() for prefix in str(self.user_path_prefixes).split(",")]

    @cached_property
    def tools(self) -> Sequence[str]:
        """Return user_path_tools as list"""
        return [tool.strip() for tool in str(self.user_path_tools).split(",")]

    @cached_property
    def user_paths(self) -> Sequence[str]:
        """Valid tool path prefixes"""
        ret = []
        for prefix in self.prefixes:
            for tool in self.tools:
                ret.append(f"{prefix}/{tool}")
        return ret

    @cached_property
    def protocols(self) -> Dict[str, Protocol]:
        """Protocols to generate URLs for, keued by config name, value is tuple for actual URL
        protocol and port"""
        ret = {}
        for name in str(self.mtx_protocols).split(","):
            protocol = name
            if name in ("hls", "webrtc"):
                protocol = "https"
            ret[name] = Protocol(protocol, getattr(self, f"mtx_{name}_port"))
        return ret
