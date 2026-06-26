"""Tests for the rmcryptpad user CRUD contract."""

from __future__ import annotations

import pytest
from conftest import build_cert_pem, rm_headers
from fastapi.testclient import TestClient

from rmcryptpad.db.user import User
from rmcryptpad.web.application import get_app_no_init


@pytest.mark.asyncio
async def test_user_created_and_updated_keep_callsign_identity(
    dbinstance: None,
) -> None:
    """Verify create and update keep user identity stable across cert refreshes."""
    _ = dbinstance
    app = get_app_no_init()
    first_cert = build_cert_pem("VIRTA-1")
    second_cert = build_cert_pem("VIRTA-1-refresh")
    separate_cert = build_cert_pem("VIRTA-2")

    with TestClient(app) as client:
        created = client.post(
            "/api/v1/users/created",
            headers=rm_headers(),
            json={"uuid": "uuid-a", "callsign": "VIRTA-1", "x509cert": first_cert},
        )
        assert created.status_code == 200
        refreshed = client.put(
            "/api/v1/users/updated",
            headers=rm_headers(),
            json={"uuid": "uuid-a", "callsign": "VIRTA-1", "x509cert": second_cert},
        )
        assert refreshed.status_code == 200
        separate = client.put(
            "/api/v1/users/updated",
            headers=rm_headers(),
            json={"uuid": "uuid-a", "callsign": "VIRTA-2", "x509cert": separate_cert},
        )
        assert separate.status_code == 200

    first = await User.by_callsign("VIRTA-1")
    second = await User.by_callsign("VIRTA-2")

    assert first.cert_pem == second_cert
    assert first.pk is not None
    assert second.pk is not None
    assert first.pk != second.pk


@pytest.mark.asyncio
async def test_user_created_accepts_cfssl_escaped_certificate_payload(
    dbinstance: None,
) -> None:
    """Verify the CRUD endpoint handles cfssl-style escaped newlines in PEM."""
    _ = dbinstance
    app = get_app_no_init()
    cert_pem = build_cert_pem("VIRTA-CFSSL")
    escaped_cert_pem = cert_pem.replace("\n", "\\n")

    with TestClient(app) as client:
        created = client.post(
            "/api/v1/users/created",
            headers=rm_headers(),
            json={
                "uuid": "uuid-cfssl",
                "callsign": "VIRTA-CFSSL",
                "x509cert": escaped_cert_pem,
            },
        )

    assert created.status_code == 200

    user = await User.by_callsign("VIRTA-CFSSL")
    assert user.cert_pem == cert_pem


@pytest.mark.asyncio
async def test_user_revoked_promoted_and_demoted_update_state(dbinstance: None) -> None:
    """Verify promote, demote, and revoke correctly update user state."""
    _ = dbinstance
    app = get_app_no_init()
    cert_pem = build_cert_pem("VIRTA-ADMIN")

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/users/promoted",
                headers=rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )

    promoted = await User.by_callsign("VIRTA-ADMIN")
    assert promoted.is_rmadmin is True

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/demoted",
                headers=rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
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
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )

    revoked = await User.by_callsign("VIRTA-ADMIN", allow_inactive=True)
    assert revoked.is_rmadmin is False
    assert revoked.revoked is not None


@pytest.mark.asyncio
async def test_wrong_rm_cn_is_forbidden_on_rm_only_routes(dbinstance: None) -> None:
    """Verify non-RM callers are rejected on RM-only endpoints."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            headers={
                "X-ClientCert-DN": "CN=not-rasenmaeher,O=RM",
                "X-SSL-Client-Verify": "SUCCESS",
            },
            json={
                "uuid": "uuid-bad",
                "callsign": "VIRTA-BAD",
                "x509cert": build_cert_pem("VIRTA-BAD"),
            },
        )
        assert response.status_code == 403
