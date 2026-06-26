"""Tests for CryptPad interop contract endpoints."""

from __future__ import annotations

import pytest
from conftest import build_cert_pem, rm_headers
from fastapi.testclient import TestClient

from rmcryptpad.db.product import Product
from rmcryptpad.web.application import get_app_no_init


def _product_headers(certcn: str) -> dict[str, str]:
    return {"X-ClientCert-DN": f"CN={certcn},O=RM", "X-SSL-Client-Verify": "SUCCESS"}


def _payload(certcn: str) -> dict[str, str]:
    return {
        "certcn": certcn,
        "x509cert": build_cert_pem(certcn),
    }


@pytest.mark.asyncio
async def test_interop_add_and_authz_return_product_credentials(
    dbinstance: None,
) -> None:
    """Verify interop add creates a product and authz returns credentials."""
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/interop/add",
            headers=rm_headers(),
            json=_payload("cryptpad.localhost"),
        )
        assert response.status_code == 200

        authz = client.get(
            "/api/v1/interop/authz", headers=_product_headers("cryptpad.localhost")
        )
        assert authz.status_code == 200
        payload = authz.json()
        assert payload["type"] == "basic"
        assert payload["username"] == "cryptpad.localhost"
        assert payload["password"]

    product = await Product.by_cn("cryptpad.localhost")
    assert product.certcn == "cryptpad.localhost"
