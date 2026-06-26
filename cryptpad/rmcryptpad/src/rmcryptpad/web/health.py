"""Healthcheck route."""

from __future__ import annotations

from fastapi import APIRouter

from ..db.user import User

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck() -> dict[str, object]:
    """Report that the service is alive and the DB is reachable."""
    users_count = 0
    async for _user in User.list(include_inactive=True):
        users_count += 1
    return {"healthy": True, "extra": f"DB works, {users_count} users found"}
