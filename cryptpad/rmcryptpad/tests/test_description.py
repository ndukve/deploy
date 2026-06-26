"""Tests for CryptPad descriptions and instructions."""

from __future__ import annotations

import pytest
from conftest import make_user_payload, rm_headers
from fastapi.testclient import TestClient

from rmcryptpad.db.errors import Deleted
from rmcryptpad.db.user import User
from rmcryptpad.web.application import get_app_no_init


def test_description_routes_return_cryptpad_metadata(dbinstance: None) -> None:
    """Verify v1 and v2 description routes return correct product metadata."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        v1 = client.get("/api/v1/description/en", headers=rm_headers())
        assert v1.status_code == 200
        assert v1.json()["shortname"] == "cryptpad"

        v2 = client.get("/api/v2/description/en", headers=rm_headers())
        assert v2.status_code == 200
        payload = v2.json()
        assert payload["shortname"] == "cryptpad"
        assert payload["component"]["ref"] == "/ui/cryptpad/remoteEntry.js"


@pytest.mark.asyncio
async def test_instructions_route_returns_product_guidance(dbinstance: None) -> None:
    """Verify instructions route returns language-specific guidance."""
    _ = dbinstance
    app = get_app_no_init()
    payload = make_user_payload("VIRTA-1")

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created", headers=rm_headers(), json=payload
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/users/revoked", headers=rm_headers(), json=payload
            ).status_code
            == 200
        )
        response = client.post(
            "/api/v1/instructions/en", headers=rm_headers(), json=payload
        )
        assert response.status_code == 200
        body = response.json()
        assert body["language"] == "en"
        assert body["instructions"]

    with pytest.raises(Deleted):
        await User.by_callsign("VIRTA-1")


def test_healthcheck_is_available(dbinstance: None) -> None:
    """Verify the health check endpoint returns healthy."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.get("/api/v1/healthcheck")
        assert response.status_code == 200
        assert response.json()["healthy"] is True
