"""APIs usable directly by the user with mTLS"""

from typing import Dict, Any, Sequence
import logging

from fastapi import APIRouter, Depends, Request
from libpvarki.middleware import MTLSHeader

from ..db.user import User
from ..schema.userdirect import UserCredentials, SRTPasswords
from ..mediamtx import MediaMTXControl
from ..config import RMMTXSettings

LOGGER = logging.getLogger(__name__)

userrouter = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


def get_callsign(request: Request) -> str:
    """extract callsign from metadata"""
    payload = request.state.mtlsdn
    return str(payload.get("CN"))


@userrouter.get("/credentials", response_model=UserCredentials)
async def get_credentials(request: Request) -> UserCredentials:
    """Get my MediaMTX credentials"""
    user = await User.by_username(get_callsign(request))
    return UserCredentials(
        username=user.username,
        password=user.mtxpassword,
        stream_ro_password=user.stream_ro_password,
    )


@userrouter.get("/srt_default", response_model=SRTPasswords)
async def get_srt_default(request: Request) -> SRTPasswords:
    """Get default SRT passwords"""
    _user = await User.by_username(get_callsign(request))
    cnf = RMMTXSettings.singleton()
    return SRTPasswords(publish=cnf.srt_pub_password, read=cnf.srt_read_password)


@userrouter.get("/streams")
async def get_streams(request: Request) -> Sequence[Dict[str, Any]]:
    """Get streams"""
    user = await User.by_username(get_callsign(request))
    conf = RMMTXSettings.singleton()
    if conf.mtx_address == "__REQUEST_HOSTNAME__":
        LOGGER.warning("Setting RMMTX_MTX_ADDRESS from the request header")
        conf.mtx_address = request.headers.get(
            "host", "__REQUEST_HOSTNAME__:1234"
        ).split(":", 1)[0]
        LOGGER.info("Setting RMMTX_MTX_ADDRESS is now: {}".format(conf.mtx_address))
    streams = await MediaMTXControl.singleton().get_paths(
        username=user.username, password=user.mtxpassword
    )
    return streams
