"""Tests for mTLS trust boundaries."""

from __future__ import annotations

import pytest
from conftest import build_cert_pem
from fastapi import Request
from fastapi.testclient import TestClient

from rmcryptpad.web.application import get_app_no_init
from rmcryptpad.web.security import require_verified_mtls_header


def _format_fingerprint_header(raw_fingerprint: str) -> str:
    return ":".join(
        raw_fingerprint[i : i + 2] for i in range(0, len(raw_fingerprint), 2)
    ).upper()


def test_missing_mtls_header_is_forbidden(dbinstance: None) -> None:
    """Verify requests without mTLS headers are rejected."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            json={
                "uuid": "uuid-a",
                "callsign": "VIRTA-1",
                "x509cert": build_cert_pem("VIRTA-1"),
            },
        )
        assert response.status_code == 403


def test_forwarded_mtls_fingerprint_is_normalized(dbinstance: None) -> None:
    """Verify forwarded fingerprint headers are normalized to lowercase hex."""
    _ = dbinstance
    app = get_app_no_init()

    @app.get("/probe")
    async def probe(request: Request) -> dict[str, str | None]:
        require_verified_mtls_header(request)
        return {"fingerprint": getattr(request.state, "mtlsfingerprint", None)}

    with TestClient(app) as client:
        response = client.get(
            "/probe",
            headers={
                "X-ClientCert-DN": "CN=VIRTA-1,O=RM",
                "X-SSL-Client-Verify": "SUCCESS",
                "X-SSL-Client-Fingerprint": _format_fingerprint_header(
                    "aabbccddeeff00112233445566778899"  # pragma: allowlist secret
                ),
            },
        )

    assert response.status_code == 200
    assert (
        response.json()["fingerprint"]
        == "aabbccddeeff00112233445566778899"  # pragma: allowlist secret
    )


@pytest.mark.asyncio
async def test_unverified_proxy_header_is_forbidden(dbinstance: None) -> None:
    """Verify unverified proxy verification header is rejected."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            headers={
                "X-ClientCert-DN": "CN=rasenmaeher,O=RM",
                "X-SSL-Client-Verify": "FAILED",
            },
            json={
                "uuid": "uuid-a",
                "callsign": "VIRTA-1",
                "x509cert": build_cert_pem("VIRTA-1"),
            },
        )
        assert response.status_code == 403
