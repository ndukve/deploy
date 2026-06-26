"""MediaMTX auth routes"""

from typing import Optional, Any, Dict
import logging

from fastapi import APIRouter, HTTPException, Response

from ..db.errors import NotFound, Deleted
from ..db.user import User
from ..db.product import Product
from ..schema.mediamtx import MTXAuthReq
from ..config import RMMTXSettings

LOGGER = logging.getLogger(__name__)

mtxrouter = APIRouter()


def authreq_redact(authreq: MTXAuthReq) -> MTXAuthReq:
    """Redact secrets if present"""
    copy = authreq.model_copy()
    if copy.password:
        copy.password = "REDACTED"  # nosec # pragma: allowlist secret
    return copy


def make_log_extra(authreq: MTXAuthReq, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Make extra logging info"""
    ret = {
        "authreq": authreq_redact(authreq).model_dump(),
    }
    ret.update(kwargs)
    return ret


def check_apiuser(authreq: MTXAuthReq) -> Optional[Response]:
    """Check if user is this API"""
    if not authreq.user or not authreq.password:
        LOGGER.debug("No user/password, returning 401")
        raise HTTPException(status_code=401)
    conf = RMMTXSettings.singleton()
    if authreq.user != conf.api_username:
        return None
    if conf.api_password == "CHANGEME":  # pragma: allowlist secret ; # nosec
        LOGGER.audit("api_password has not been changed from default, disallowing use")  # type: ignore[attr-defined]
        raise HTTPException(status_code=401)
    if authreq.password != conf.api_password:
        raise HTTPException(status_code=401)
    return Response(status_code=204)


async def check_productuser(authreq: MTXAuthReq) -> Optional[Response]:
    """Check if the user is a product that requested interop"""
    if not authreq.user or not authreq.password:
        LOGGER.debug("No user/password, returning 401")
        raise HTTPException(status_code=401)
    try:
        dbproduct = await Product.by_cn(authreq.user)
        if authreq.password not in (
            dbproduct.mtxpassword,
            dbproduct.stream_ro_password,
        ):
            LOGGER.audit(  # type: ignore[attr-defined]
                "Wrong password for {}".format(authreq.user),
                extra=make_log_extra(authreq),
            )
            raise HTTPException(status_code=403)
        if authreq.password == dbproduct.stream_ro_password:
            if authreq.action not in ("read", "playback"):
                LOGGER.audit(  # type: ignore[attr-defined]
                    "read-only {} requesting {}".format(authreq.user, authreq.action),
                    extra=make_log_extra(authreq),
                )
                raise HTTPException(status_code=403)
        # By default products are allowed to do everything
        return Response(status_code=204)
    except (NotFound, Deleted):
        pass
    return None


def user_publish_path_rules(authreq: MTXAuthReq, dbuser: User) -> Optional[Response]:
    """Rules for publishing"""
    conf = RMMTXSettings.singleton()
    path_prefix_matched = False
    if authreq.path is None:
        LOGGER.error("Path cannot be None")
        raise HTTPException(status_code=403)
    for prefix in conf.user_paths:
        if authreq.path.startswith(f"{prefix}/{dbuser.username}"):
            path_prefix_matched = True
            break
    if not path_prefix_matched:
        LOGGER.audit(  # type: ignore[attr-defined]
            "{} is not allowed to {} on {}".format(
                authreq.user, authreq.action, authreq.path
            ),
            extra=make_log_extra(authreq),
        )
        raise HTTPException(status_code=403)
    return Response(status_code=204)


def ro_rules(authreq: MTXAuthReq, dbuser: User) -> Optional[Response]:
    """Rules for using the read-only password for user"""
    # Only read/playback is allowed
    if authreq.action not in ("read", "playback"):
        LOGGER.audit(  # type: ignore[attr-defined]
            "read-only {} requesting {}".format(authreq.user, authreq.action),
            extra=make_log_extra(authreq),
        )
        raise HTTPException(status_code=403)
    # Use same path rules as for publish for the specific RO password
    if resp := user_publish_path_rules(authreq, dbuser):
        return resp
    LOGGER.audit(  # type: ignore[attr-defined]
        "read-only permissions check for {} fell through, deny-by-default".format(
            authreq.user
        ),
        extra=make_log_extra(authreq),
    )
    raise HTTPException(status_code=403)


async def check_rmuser(authreq: MTXAuthReq) -> Optional[Response]:
    """Check RM user credentials"""
    if not authreq.user or not authreq.password:
        LOGGER.debug("No user/password, returning 401")
        raise HTTPException(status_code=401)
    try:
        dbuser = await User.by_username(authreq.user)
        if authreq.password not in (dbuser.mtxpassword, dbuser.stream_ro_password):
            LOGGER.audit(  # type: ignore[attr-defined]
                "Wrong password for {}".format(authreq.user),
                extra=make_log_extra(authreq),
            )
            raise HTTPException(status_code=403)
        if dbuser.is_rmadmin:
            LOGGER.audit(  # type: ignore[attr-defined]
                "{} is admin, allowing everything".format(authreq.user),
                extra=make_log_extra(authreq),
            )
            return Response(status_code=204)
        # Operations that require admin privileges
        if authreq.action in ("api", "metrics", "pprof") and not dbuser.is_rmadmin:
            LOGGER.audit(  # type: ignore[attr-defined]
                "{} is not admin requesting {}".format(authreq.user, authreq.action),
                extra=make_log_extra(authreq),
            )
            raise HTTPException(status_code=403)
        # read-only rules
        if authreq.password == dbuser.stream_ro_password:
            if resp := ro_rules(authreq, dbuser):
                return resp

        # User path based rules
        if authreq.action in ("read", "playback"):
            # Reads are allowed
            return Response(status_code=204)
        if authreq.action == "publish":
            # Publishing has specific rules
            if resp := user_publish_path_rules(authreq, dbuser):
                return resp
        # Checks fell through
        LOGGER.audit(  # type: ignore[attr-defined]
            "User permissions check for {} fell through, deny-by-default".format(
                authreq.user
            ),
            extra=make_log_extra(authreq),
        )
        raise HTTPException(status_code=403)
    except (NotFound, Deleted) as exc:
        LOGGER.audit(  # type: ignore[attr-defined]
            "Invalid user {}: {}".format(authreq.user, exc),
            extra=make_log_extra(authreq),
        )
        raise HTTPException(status_code=403) from exc


@mtxrouter.post("/auth")
async def get_auth(authreq: MTXAuthReq) -> Response:
    """Check if username and password match and return empty ok if so"""
    LOGGER.debug("Processing {}".format(authreq_redact(authreq)))
    if not authreq.user or not authreq.password:
        LOGGER.debug("No user/password, returning 401")
        raise HTTPException(status_code=401)
    if resp := check_apiuser(authreq):
        return resp
    if resp := await check_productuser(authreq):
        return resp
    if resp := await check_rmuser(authreq):
        return resp
    LOGGER.audit(  # type: ignore[attr-defined]
        "Fell through the checks, this should not happen", extra=make_log_extra(authreq)
    )
    raise HTTPException(status_code=403)
