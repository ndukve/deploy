"""User lifecycle contract routes."""

from __future__ import annotations

import datetime
import logging

from fastapi import APIRouter, Depends, Request

from ..db.engine import EngineWrapper
from ..db.errors import NotFound
from ..db.user import User
from ..schema import OperationResultResponse, UserCRUDRequest
from .security import require_rm_caller, require_verified_mtls_header

LOGGER = logging.getLogger(__name__)

crudrouter = APIRouter(dependencies=[Depends(require_verified_mtls_header)])


@crudrouter.post("/created", response_model=OperationResultResponse)
async def user_created(
    user: UserCRUDRequest, request: Request
) -> OperationResultResponse:
    """Create or refresh a callsign."""
    require_rm_caller(request)
    await User.create_or_update(
        callsign=user.callsign, rmuuid=user.uuid, cert_pem=user.x509cert
    )
    return OperationResultResponse(success=True)


@crudrouter.post("/revoked", response_model=OperationResultResponse)
async def user_revoked(
    user: UserCRUDRequest, request: Request
) -> OperationResultResponse:
    """Revoke a callsign."""
    require_rm_caller(request)
    try:
        dbuser = await User.by_callsign(user.callsign, allow_inactive=True)
    except NotFound:
        dbuser = await User.create_or_update(
            callsign=user.callsign, rmuuid=user.uuid, cert_pem=user.x509cert
        )
    dbuser.revoked = datetime.datetime.now(datetime.UTC)
    with EngineWrapper.get_session() as session:
        session.add(dbuser)
        session.commit()
        session.refresh(dbuser)
    return OperationResultResponse(success=True)


@crudrouter.post("/promoted", response_model=OperationResultResponse)
async def user_promoted(
    user: UserCRUDRequest, request: Request
) -> OperationResultResponse:
    """Promote a callsign to admin."""
    require_rm_caller(request)
    await User.create_or_update(
        callsign=user.callsign,
        rmuuid=user.uuid,
        cert_pem=user.x509cert,
        is_rmadmin=True,
    )
    return OperationResultResponse(success=True)


@crudrouter.post("/demoted", response_model=OperationResultResponse)
async def user_demoted(
    user: UserCRUDRequest, request: Request
) -> OperationResultResponse:
    """Demote a callsign from admin."""
    require_rm_caller(request)
    await User.create_or_update(
        callsign=user.callsign,
        rmuuid=user.uuid,
        cert_pem=user.x509cert,
        is_rmadmin=False,
    )
    return OperationResultResponse(success=True)


@crudrouter.put("/updated", response_model=OperationResultResponse)
async def user_updated(
    user: UserCRUDRequest, request: Request
) -> OperationResultResponse:
    """Refresh a callsign without migrating identity."""
    require_rm_caller(request)
    await User.create_or_update(
        callsign=user.callsign, rmuuid=user.uuid, cert_pem=user.x509cert
    )
    return OperationResultResponse(success=True)
