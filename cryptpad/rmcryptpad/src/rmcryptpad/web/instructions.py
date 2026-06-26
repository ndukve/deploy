"""Instructions routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..schema import InstructionsResponse, UserCRUDRequest
from .security import require_rm_caller, require_verified_mtls_header

router = APIRouter(dependencies=[Depends(require_verified_mtls_header)])


@router.post("/instructions/{language}", response_model=InstructionsResponse)
async def user_instructions(
    user: UserCRUDRequest, request: Request, language: str
) -> InstructionsResponse:
    """Return product guidance for the current callsign."""
    require_rm_caller(request)
    return InstructionsResponse(
        callsign=user.callsign,
        language=language,
        instructions=(
            "Open CryptPad through the Deploy App mTLS host"
            " and keep the certificate-backed account in sync."
        ),
    )
