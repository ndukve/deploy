"""Endpoints for information for the admin"""

from typing import Optional
import logging
import os

from fastapi import APIRouter, Depends, Request
from libpvarki.middleware import MTLSHeader
from libpvarki.schemas.product import ProductHealthCheckResponse

LOGGER = logging.getLogger(__name__)

mtls_router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])
router = APIRouter()


@router.get("")
async def get_healthcheck_delivery_status(
    request: Request,
) -> ProductHealthCheckResponse:
    """Return 200 when api is ready to deliver"""
    ready_to_serve: bool = False
    reason: Optional[str] = None

    # TODO do some actual logic to check if we have something to serve...
    # FIXME: If using this, at least use pathlib...
    dir_files = os.listdir("/opt/tak/data/certs/files")
    if len(dir_files) > 0:
        ready_to_serve = True

    if not ready_to_serve:
        reason = "Waiting for RM to give go ahead."
        LOGGER.info("{} : {}".format(request.url, reason))

    return ProductHealthCheckResponse(healthy=ready_to_serve, extra=reason)
