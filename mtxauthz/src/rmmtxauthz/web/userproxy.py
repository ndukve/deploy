"""APIs usable through proxy with RM"""

from typing import Dict, Any, Sequence
import logging

from fastapi import APIRouter, Depends, Request
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import UserCRUDRequest
from rmmtxauthz.web.usercrud import comes_from_rm


from ..db.user import User
from ..schema.userdirect import UserCredentials, SRTPasswords
from ..mediamtx import MediaMTXControl
from ..config import RMMTXSettings

LOGGER = logging.getLogger(__name__)

userrouterproxy = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@userrouterproxy.post("/credentials", response_model=UserCredentials)
async def get_credentials(
    request: Request, user_request: UserCRUDRequest
) -> UserCredentials:
    """Get my MediaMTX credentials"""
    comes_from_rm(request, allow_proxy=True)
    user = await User.by_username(user_request.callsign)
    return UserCredentials(
        username=user.username,
        password=user.mtxpassword,
        stream_ro_password=user.stream_ro_password,
    )


@userrouterproxy.post("/srt_default", response_model=SRTPasswords)
async def get_srt_default(
    request: Request, user_request: UserCRUDRequest
) -> SRTPasswords:
    """Get default SRT passwords"""
    comes_from_rm(request, allow_proxy=True)
    _user = await User.by_username(user_request.callsign)
    cnf = RMMTXSettings.singleton()
    return SRTPasswords(publish=cnf.srt_pub_password, read=cnf.srt_read_password)


@userrouterproxy.post("/streams")
async def get_streams(
    request: Request, user_request: UserCRUDRequest
) -> Sequence[Dict[str, Any]]:
    """Get streams"""
    comes_from_rm(request, allow_proxy=True)
    user = await User.by_username(user_request.callsign)
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
