"""MediaMTX schemas"""

from __future__ import annotations
from typing import Optional
import logging

from pydantic import BaseModel, Field, ConfigDict

LOGGER = logging.getLogger(__name__)


class MTXAuthReq(BaseModel):
    """
    https://github.com/bluenviron/mediamtx?tab=readme-ov-file#http-based
    {
      "user": "user",
      "password": "password",  # pragma: allowlist secret
      "ip": "ip",
      "action": "publish|read|playback|api|metrics|pprof",
      "path": "path",
      "protocol": "rtsp|rtmp|hls|webrtc|srt",
      "id": "id",
      "query": "query"
    }
    """

    model_config = ConfigDict(extra="ignore")

    user: Optional[str] = Field(
        description="Username, may be empty if user is not provided yet", default=None
    )
    password: Optional[str] = Field(
        description="Password, may be empty if user+password is not provided yet",
        default=None,
        repr=False,
    )
    ip: Optional[str] = Field(
        description="IP address of the client from MediaMTX PoV", default=None
    )
    action: Optional[str] = Field(description="Action user wants to take", default=None)
    path: Optional[str] = Field(description="Path user wants to use", default=None)
    protocol: Optional[str] = Field(
        description="Protocol user wants to use", default=None
    )
    id: Optional[str] = Field(
        description="FIXME: Figure out what this actually means", default=None
    )
    query: Optional[str] = Field(
        description="FIXME: Figure out what this actually means", default=None
    )
