"""Tests for client data contract endpoints."""

from __future__ import annotations

import pytest
from conftest import make_user_payload, rm_headers
from fastapi.testclient import TestClient

from rmcryptpad.db.errors import Deleted
from rmcryptpad.db.user import User
from rmcryptpad.web.application import get_app_no_init


def test_client_data_routes_return_settings_urls(dbinstance: None) -> None:
    """Verify both client data endpoints return correct CryptPad URLs."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        for path in ("/api/v2/clients/data", "/api/v2/admin/clients/data"):
            response = client.post(
                path, headers=rm_headers(), json=make_user_payload("VIRTA-1")
            )
            assert response.status_code == 200
            payload = response.json()["data"]
            assert payload["url"] == "https://cryptpad.localhost:8443"
            assert payload["sandbox_url"] == "https://sandbox.cryptpad.localhost:8443"
            assert payload["docs_url"]
            assert payload["oidc_issuer"] == "https://rmcryptpad.localhost:8443"


@pytest.mark.asyncio
async def test_revoked_user_stays_revoked_after_client_data_access(
    dbinstance: None,
) -> None:
    """Ensure accessing client data does not re-enable a revoked user."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        client.post(
            "/api/v1/users/created",
            headers=rm_headers(),
            json=make_user_payload("VIRTA-REVOKED"),
        )
        client.post(
            "/api/v1/users/revoked",
            headers=rm_headers(),
            json=make_user_payload("VIRTA-REVOKED"),
        )
        response = client.post(
            "/api/v2/clients/data",
            headers=rm_headers(),
            json=make_user_payload("VIRTA-REVOKED"),
        )
        assert response.status_code == 200

    with pytest.raises(Deleted):
        await User.by_callsign("VIRTA-REVOKED")
