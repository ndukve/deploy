"""OIDC provider routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

from ..oidc import OIDCProvider
from .security import require_verified_mtls_header

router = APIRouter()


@router.get("/.well-known/openid-configuration")
async def discovery() -> JSONResponse:
    """Return the OIDC discovery document."""
    return JSONResponse(OIDCProvider().discovery_document())


@router.get("/oidc/jwks.json")
async def jwks() -> JSONResponse:
    """Return the OIDC JSON Web Key Set."""
    return JSONResponse(OIDCProvider().jwks_document())


@router.get("/oidc/authorize", dependencies=[Depends(require_verified_mtls_header)])
async def authorize(request: Request) -> RedirectResponse:
    """Handle OIDC authorization requests."""
    return await OIDCProvider().authorize(request)


@router.post("/oidc/token")
async def token(request: Request) -> JSONResponse:
    """Exchange an authorization code for tokens."""
    return JSONResponse(await OIDCProvider().token(request))


@router.get("/oidc/userinfo")
async def userinfo(request: Request) -> JSONResponse:
    """Return user info for the authenticated token."""
    return JSONResponse(await OIDCProvider().userinfo(request))
