""" "User actions"""

import logging
from fastapi import APIRouter, Depends
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import UserCRUDRequest
from libpvarki.schemas.generic import OperationResultResponse

from takrmapi.takutils import tak_helpers

LOGGER = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])

test_router = APIRouter()


@router.post("/created")
async def user_created(user: UserCRUDRequest) -> OperationResultResponse:
    """New device cert was created"""
    tak_usercrud = tak_helpers.UserCRUD(user)
    LOGGER.info("Adding new user '{}' to TAK".format(user.callsign))
    await tak_usercrud.add_new_user()

    result = OperationResultResponse(success=True)
    return result


# While delete would be semantically better it takes no body and definitely forces the
# integration layer to keep track of UUIDs
@router.post("/revoked")
async def user_revoked(user: UserCRUDRequest) -> OperationResultResponse:
    """Device cert was revoked"""
    tak_usercrud = tak_helpers.UserCRUD(user)
    LOGGER.info("Removing user '{}' from TAK".format(user.callsign))
    await tak_usercrud.revoke_user()
    result = OperationResultResponse(success=True)
    return result


@router.post("/promoted")
async def user_promoted(user: UserCRUDRequest) -> OperationResultResponse:
    """Device cert was promoted to admin privileges"""
    tak_usercrud = tak_helpers.UserCRUD(user)
    LOGGER.info("Promoting user '{}' to admin".format(user.callsign))
    await tak_usercrud.promote_user()
    result = OperationResultResponse(success=True)
    return result


@router.post("/demoted")
async def user_demoted(user: UserCRUDRequest) -> OperationResultResponse:
    """Device cert was demoted to standard privileges"""
    tak_usercrud = tak_helpers.UserCRUD(user)
    LOGGER.info("Demoting user '{}' to normal user".format(user.callsign))
    await tak_usercrud.demote_user()
    result = OperationResultResponse(success=True)
    return result


@router.put("/updated")
async def user_updated(user: UserCRUDRequest) -> OperationResultResponse:
    """Device callsign updated"""
    tak_usercrud = tak_helpers.UserCRUD(user)
    await tak_usercrud.update_user()
    result = OperationResultResponse(success=True)
    return result
