"""Tests for the CryptPad OIDC provider."""

from __future__ import annotations

import base64
import hashlib
import urllib.parse
from pathlib import Path

import pytest
from conftest import build_cert_pem, rm_headers
from fastapi.testclient import TestClient

from rmcryptpad.config import RMCryptPadSettings
from rmcryptpad.db.user import fingerprint_pem
from rmcryptpad.oidc.keys import OIDCKeyManager
from rmcryptpad.web.application import get_app_no_init


def _user_headers(callsign: str) -> dict[str, str]:
    return {"X-ClientCert-DN": f"CN={callsign},O=RM", "X-SSL-Client-Verify": "SUCCESS"}


def _fingerprint_header(cert_pem: str) -> str:
    fingerprint = fingerprint_pem(cert_pem)
    return ":".join(
        fingerprint[i : i + 2] for i in range(0, len(fingerprint), 2)
    ).upper()


def _configure_oidc(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMCRYPTPAD_OIDC_KEY_DIR", str(tmp_path))
    monkeypatch.setenv("RMCRYPTPAD_OIDC_ISSUER", "https://rmcryptpad.localhost:8443")
    monkeypatch.setenv("RMCRYPTPAD_OIDC_CLIENT_ID", "cryptpad")
    monkeypatch.setenv("RMCRYPTPAD_OIDC_CLIENT_SECRET", "cryptpad-secret")
    monkeypatch.setenv("RMCRYPTPAD_OIDC_CODE_TTL_SECONDS", "300")
    monkeypatch.setenv("RMCRYPTPAD_OIDC_TOKEN_TTL_SECONDS", "3600")
    RMCryptPadSettings._singleton = None  # pylint: disable=protected-access
    OIDCKeyManager._singleton = None  # pylint: disable=protected-access


def _pkce_pair() -> tuple[str, str]:
    verifier = "correct-horse-battery-staple"
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
    )
    return verifier, challenge


def test_discovery_document_returns_expected_urls(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify the OIDC discovery document contains correct endpoint URLs."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.get("/.well-known/openid-configuration")

    assert response.status_code == 200
    payload = response.json()
    assert payload["issuer"] == "https://rmcryptpad.localhost:8443"
    assert payload["authorization_endpoint"].endswith("/oidc/authorize")
    assert payload["token_endpoint"].endswith("/oidc/token")
    assert payload["userinfo_endpoint"].endswith("/oidc/userinfo")
    assert payload["jwks_uri"].endswith("/oidc/jwks.json")


def test_authorize_rejects_missing_or_revoked_active_callsign(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify authorize rejects unknown and revoked callsigns."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()
    cert_pem = build_cert_pem("VIRTA-REVOKED")

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={
                    "uuid": "uuid-1",
                    "callsign": "VIRTA-REVOKED",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/users/revoked",
                headers=rm_headers(),
                json={
                    "uuid": "uuid-1",
                    "callsign": "VIRTA-REVOKED",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )
        missing = client.get("/oidc/authorize")
        revoked = client.get(
            "/oidc/authorize",
            headers=_user_headers("VIRTA-REVOKED"),
            params={
                "client_id": "cryptpad",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "response_type": "code",
                "scope": "openid profile",
                "code_challenge": "abc",
                "code_challenge_method": "S256",
                "nonce": "nonce-a",
                "state": "state-a",
            },
        )

    assert missing.status_code == 403
    assert revoked.status_code == 403


def test_authorize_issues_code_for_active_callsign(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify authorize redirects with an authorization code for active users."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()
    cert_pem = build_cert_pem("VIRTA-1")
    verifier, challenge = _pkce_pair()

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={"uuid": "uuid-1", "callsign": "VIRTA-1", "x509cert": cert_pem},
            ).status_code
            == 200
        )
        response = client.get(
            "/oidc/authorize",
            headers=_user_headers("VIRTA-1"),
            params={
                "client_id": "cryptpad",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "response_type": "code",
                "scope": "openid profile",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "nonce": "nonce-a",
                "state": "state-a",
            },
            follow_redirects=False,
        )

    assert response.status_code in {302, 303}
    location = response.headers["location"]
    parsed = urllib.parse.urlparse(location)
    query = urllib.parse.parse_qs(parsed.query)
    assert parsed.netloc == "cryptpad.localhost"
    assert query["state"] == ["state-a"]
    assert query["code"]
    assert verifier


def test_authorize_rejects_mismatched_certificate_fingerprint(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify authorize rejects requests with wrong certificate fingerprint."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()
    active_cert = build_cert_pem("VIRTA-1")
    wrong_cert = build_cert_pem("VIRTA-1")
    _, challenge = _pkce_pair()

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={"uuid": "uuid-1", "callsign": "VIRTA-1", "x509cert": active_cert},
            ).status_code
            == 200
        )
        response = client.get(
            "/oidc/authorize",
            headers={
                **_user_headers("VIRTA-1"),
                "X-SSL-Client-Fingerprint": _fingerprint_header(wrong_cert),
            },
            params={
                "client_id": "cryptpad",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "response_type": "code",
                "scope": "openid profile",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "nonce": "nonce-a",
                "state": "state-a",
            },
            follow_redirects=False,
        )

    assert response.status_code == 403


def test_authorize_rejects_wrong_callsign(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify authorize rejects a callsign that doesn't match any user."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()
    active_cert = build_cert_pem("VIRTA-1")
    wrong_headers = _user_headers("VIRTA-2")

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={"uuid": "uuid-1", "callsign": "VIRTA-1", "x509cert": active_cert},
            ).status_code
            == 200
        )
        response = client.get(
            "/oidc/authorize",
            headers=wrong_headers,
            params={
                "client_id": "cryptpad",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "response_type": "code",
                "scope": "openid profile",
                "code_challenge": "abc",
                "code_challenge_method": "S256",
                "nonce": "nonce-a",
                "state": "state-a",
            },
        )

    assert response.status_code == 403


def test_token_exchange_and_userinfo_work_with_pkce_and_basic_auth(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify full OIDC flow: authorize, token exchange, and userinfo."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()
    cert_pem = build_cert_pem("VIRTA-1")
    verifier, challenge = _pkce_pair()

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={"uuid": "uuid-1", "callsign": "VIRTA-1", "x509cert": cert_pem},
            ).status_code
            == 200
        )
        authz = client.get(
            "/oidc/authorize",
            headers=_user_headers("VIRTA-1"),
            params={
                "client_id": "cryptpad",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "response_type": "code",
                "scope": "openid profile",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "nonce": "nonce-a",
                "state": "state-a",
            },
            follow_redirects=False,
        )
        code = urllib.parse.parse_qs(
            urllib.parse.urlparse(authz.headers["location"]).query
        )["code"][0]
        token = client.post(
            "/oidc/token",
            auth=("cryptpad", "cryptpad-secret"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "code_verifier": verifier,
            },
        )

    assert token.status_code == 200
    payload = token.json()
    assert payload["token_type"] == "Bearer"
    assert payload["access_token"]
    assert payload["id_token"]

    with TestClient(app) as client:
        userinfo = client.get(
            "/oidc/userinfo",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )

    assert userinfo.status_code == 200
    claims = userinfo.json()
    assert claims["sub"] == "VIRTA-1"
    assert claims["preferred_username"] == "VIRTA-1"
    assert claims["name"] == "VIRTA-1"
    assert claims["nonce"] == "nonce-a"


def test_token_rejects_reuse_and_invalid_code(
    dbinstance: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify authorization codes cannot be reused and invalid codes are rejected."""
    _ = dbinstance
    _configure_oidc(monkeypatch, tmp_path)
    app = get_app_no_init()
    cert_pem = build_cert_pem("VIRTA-1")
    verifier, challenge = _pkce_pair()

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={"uuid": "uuid-1", "callsign": "VIRTA-1", "x509cert": cert_pem},
            ).status_code
            == 200
        )
        authz = client.get(
            "/oidc/authorize",
            headers=_user_headers("VIRTA-1"),
            params={
                "client_id": "cryptpad",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "response_type": "code",
                "scope": "openid profile",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "nonce": "nonce-a",
                "state": "state-a",
            },
            follow_redirects=False,
        )
        code = urllib.parse.parse_qs(
            urllib.parse.urlparse(authz.headers["location"]).query
        )["code"][0]
        first = client.post(
            "/oidc/token",
            auth=("cryptpad", "cryptpad-secret"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "code_verifier": verifier,
            },
        )
        second = client.post(
            "/oidc/token",
            auth=("cryptpad", "cryptpad-secret"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "code_verifier": verifier,
            },
        )
        invalid = client.post(
            "/oidc/token",
            auth=("cryptpad", "cryptpad-secret"),
            data={
                "grant_type": "authorization_code",
                "code": "not-a-code",
                "redirect_uri": "https://cryptpad.localhost/ssoauth",
                "code_verifier": verifier,
            },
        )

    assert first.status_code == 200
    assert second.status_code in {400, 401}
    assert invalid.status_code in {400, 401}
