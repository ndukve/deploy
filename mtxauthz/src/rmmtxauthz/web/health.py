"""Health check"""

import logging

from fastapi import APIRouter
from libpvarki.schemas.product import ProductHealthCheckResponse

from ..db.user import User

LOGGER = logging.getLogger(__name__)

hrouter = APIRouter()


@hrouter.get("/healthcheck")
async def request_healthcheck() -> ProductHealthCheckResponse:
    """Check that we are healthy, return accordingly"""
    users_count = 0
    async for _user in User.list():
        users_count += 1
    return ProductHealthCheckResponse(
        healthy=True, extra=f"DB works, {users_count} users found"
    )
