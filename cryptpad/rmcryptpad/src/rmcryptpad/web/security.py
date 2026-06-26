"""Lightweight mTLS header helpers."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from ..config import RMCryptPadSettings

CLIENT_DN_HEADER = "X-ClientCert-DN"
CLIENT_FINGERPRINT_HEADER = "X-SSL-Client-Fingerprint"
CLIENT_VERIFY_HEADER = "X-SSL-Client-Verify"
CLIENT_VERIFY_SUCCESS = "SUCCESS"


def extract_cn(distinguished_name: str) -> str | None:
    """Extract the CN component from a distinguished name string."""
    for part in distinguished_name.split(","):
        key, sep, value = part.partition("=")
        if key.strip().upper() == "CN" and sep:
            return value.strip()
    return None


def normalize_client_fingerprint(fingerprint: str | None) -> str | None:
    """Normalize forwarded fingerprints to lowercase hex without separators."""
    if not fingerprint:
        return None
    return "".join(
        character for character in fingerprint if character not in ": \t\r\n"
    ).lower()


def require_mtls_header(request: Request) -> str:
    """Require a forwarded client certificate DN header."""
    dn = request.headers.get(CLIENT_DN_HEADER)
    if not dn:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing client certificate header",
        )
    request.state.mtlsdn = {"DN": dn, "CN": extract_cn(dn) or dn.strip()}
    request.state.mtlsfingerprint = normalize_client_fingerprint(
        request.headers.get(CLIENT_FINGERPRINT_HEADER)
    )
    return dn


def require_verified_mtls_header(request: Request) -> str:
    """Require a forwarded client certificate DN header and a trusted proxy verification signal."""
    dn = require_mtls_header(request)
    if request.headers.get(CLIENT_VERIFY_HEADER) != CLIENT_VERIFY_SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unverified client certificate",
        )
    request.state.mtlsverified = True
    return dn


def get_client_cn(request: Request) -> str:
    """Return the forwarded client CN."""
    payload: dict[str, str] | None = getattr(request.state, "mtlsdn", None)
    if payload and payload.get("CN"):
        return payload["CN"]
    dn = require_verified_mtls_header(request)
    return extract_cn(dn) or dn.strip()


def require_rm_caller(request: Request) -> None:
    """Ensure the caller is the Rasenmaeher control plane."""
    if get_client_cn(request) != RMCryptPadSettings.singleton().rmcn:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
