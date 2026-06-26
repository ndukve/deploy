"""OIDC service logic for rmcryptpad."""

from __future__ import annotations

import base64
import datetime
import hashlib
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse

from ..config import RMCryptPadSettings
from ..db.errors import Deleted, NotFound
from ..db.oidc_code import OIDCAuthorizationCode
from ..db.user import User
from ..web.security import normalize_client_fingerprint
from .keys import OIDCKeyManager


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _sha256_b64url(value: str) -> str:
    return _b64url(hashlib.sha256(value.encode("utf-8")).digest())


def _parse_basic_auth(header: str | None) -> tuple[str | None, str | None]:
    if not header or not header.startswith("Basic "):
        return None, None
    try:
        raw = base64.b64decode(header[6:].encode("utf-8")).decode("utf-8")
        client_id, client_secret = raw.split(":", 1)
        return client_id, client_secret
    except (ValueError, UnicodeDecodeError):  # pragma: no cover - defensive parse guard
        return None, None


def _parse_form(body: bytes) -> dict[str, str]:
    parsed = urllib.parse.parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] for key, values in parsed.items()}


@dataclass
class OIDCProvider:
    """Minimal in-house OIDC provider."""

    settings: RMCryptPadSettings = field(default_factory=RMCryptPadSettings.singleton)
    keys: OIDCKeyManager = field(default_factory=OIDCKeyManager.singleton)

    @property
    def issuer(self) -> str:
        """Return the OIDC issuer URL."""
        return self.settings.oidc_issuer.rstrip("/")

    def discovery_document(self) -> dict[str, Any]:
        """Return the OpenID Connect discovery document."""
        return {
            "issuer": self.issuer,
            "authorization_endpoint": f"{self.issuer}/oidc/authorize",
            "token_endpoint": f"{self.issuer}/oidc/token",
            "userinfo_endpoint": f"{self.issuer}/oidc/userinfo",
            "jwks_uri": f"{self.issuer}/oidc/jwks.json",
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "grant_types_supported": ["authorization_code"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
            "code_challenge_methods_supported": ["S256"],
            "scopes_supported": ["openid", "profile"],
            "claims_supported": ["sub", "preferred_username", "name", "nonce", "scope"],
        }

    def jwks_document(self) -> dict[str, list[dict[str, Any]]]:
        """Return the JSON Web Key Set."""
        return {"keys": [self.keys.public_jwk()]}

    async def authorize(self, request: Request) -> RedirectResponse:
        """Handle an OIDC authorization request and redirect with a code."""
        cn = getattr(getattr(request.state, "mtlsdn", {}), "get", lambda *_: None)("CN")
        if not cn:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Missing client identity"
            )
        try:
            user = await User.by_callsign(cn)
        except (NotFound, Deleted):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Inactive callsign"
            ) from None
        request_fingerprint = normalize_client_fingerprint(
            getattr(request.state, "mtlsfingerprint", None)
        )
        if (
            request_fingerprint
            and user.cert_fingerprint
            and request_fingerprint != user.cert_fingerprint
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Certificate fingerprint mismatch",
            )
        params = request.query_params
        if params.get("response_type") != "code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported response_type",
            )
        if params.get("client_id") != self.settings.oidc_client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown client_id"
            )
        redirect_uri = params.get("redirect_uri")
        if not redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing redirect_uri"
            )
        code_challenge = params.get("code_challenge")
        code_challenge_method = params.get("code_challenge_method") or "S256"
        if code_challenge_method != "S256" or not code_challenge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="PKCE S256 required"
            )
        code = await OIDCAuthorizationCode.issue(
            callsign=user.callsign,
            client_id=self.settings.oidc_client_id,
            redirect_uri=redirect_uri,
            expires_at=_now()
            + datetime.timedelta(seconds=self.settings.oidc_code_ttl_seconds),
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=params.get("nonce"),
            scope=params.get("scope") or "openid profile",
        )
        query: dict[str, str] = {"code": code}
        state = params.get("state")
        if state:
            query["state"] = state
        location = f"{redirect_uri}?{urllib.parse.urlencode(query)}"
        return RedirectResponse(url=location, status_code=status.HTTP_302_FOUND)

    async def token(self, request: Request) -> dict[str, Any]:
        """Exchange an authorization code for access and ID tokens."""
        form = _parse_form(await request.body())
        header_client_id, header_client_secret = _parse_basic_auth(
            request.headers.get("authorization")
        )
        client_id = form.get("client_id") or header_client_id
        client_secret = form.get("client_secret") or header_client_secret
        if (
            client_id != self.settings.oidc_client_id
            or client_secret != self.settings.oidc_client_secret
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
            )
        if form.get("grant_type") != "authorization_code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported grant_type"
            )
        code = form.get("code")
        redirect_uri = form.get("redirect_uri")
        code_verifier = form.get("code_verifier")
        if not code or not redirect_uri or not code_verifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing token request fields",
            )
        try:
            code_row = await OIDCAuthorizationCode.consume(
                code=code,
                client_id=self.settings.oidc_client_id,
                redirect_uri=redirect_uri,
            )
        except (NotFound, Deleted):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant"
            ) from None
        if (
            code_row.code_challenge_method == "S256"
            and _sha256_b64url(code_verifier) != code_row.code_challenge
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant"
            )
        if code_row.code_challenge_method not in {None, "S256"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant"
            )
        try:
            user = await User.by_callsign(code_row.callsign)
        except (NotFound, Deleted):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant"
            ) from None
        jwt_header = {"alg": "RS256", "kid": self.keys.kid, "typ": "JWT"}
        access_token = self.keys.sign_jwt(
            jwt_header,
            self._base_claims(user.callsign, code_row.nonce, code_row.scope, "access"),
        )
        id_token = self.keys.sign_jwt(
            jwt_header,
            self._base_claims(user.callsign, code_row.nonce, code_row.scope, "id"),
        )
        return {
            "access_token": access_token,
            "id_token": id_token,
            "token_type": "Bearer",
            "expires_in": self.settings.oidc_token_ttl_seconds,
            "scope": code_row.scope,
        }

    async def userinfo(self, request: Request) -> dict[str, Any]:
        """Return user claims for a valid access token."""
        authorization = request.headers.get("authorization") or ""
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token"
            )
        token = authorization.removeprefix("Bearer ").strip()
        try:
            claims = self.keys.verify_jwt(token)
        except Exception as exc:  # pragma: no cover - defensive verify guard
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            ) from exc
        if claims.get("iss") != self.issuer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        if claims.get("token_use") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        if int(claims.get("exp", 0)) <= int(_now().timestamp()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        return {
            "sub": claims["sub"],
            "preferred_username": claims["preferred_username"],
            "name": claims["name"],
            "nonce": claims.get("nonce"),
            "scope": claims.get("scope"),
        }

    def _base_claims(
        self, callsign: str, nonce: str | None, scope: str, token_use: str
    ) -> dict[str, Any]:
        now = int(_now().timestamp())
        return {
            "iss": self.issuer,
            "sub": callsign,
            "aud": self.settings.oidc_client_id,
            "iat": now,
            "exp": now + self.settings.oidc_token_ttl_seconds,
            "nonce": nonce,
            "scope": scope,
            "preferred_username": callsign,
            "name": callsign,
            "token_use": token_use,
        }
