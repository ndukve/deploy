"""Test the interop endpoints"""

import logging

import pytest
from fastapi.testclient import TestClient

from rmmtxauthz.schema.interop import ProductAddRequest, ProductAuthzResponse
from rmmtxauthz.db.product import Product

LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_add(dbinstance: None, testclient: TestClient) -> None:
    """Test adding of product"""
    _ = dbinstance
    req = ProductAddRequest(
        certcn="fake.localmaeher.dev.pvarki.fi",
        x509cert="-----BEGIN CERTIFICATE-----\\nMIIEwjCC...\\n-----END CERTIFICATE-----\\n",
    )
    payload = req.model_dump()
    resp = testclient.post("/api/v1/interop/add", json=payload)
    assert resp.status_code == 200
    dbproduct = await Product.by_cn("fake.localmaeher.dev.pvarki.fi")
    assert dbproduct


@pytest.mark.asyncio
async def test_authz(dbinstance: None, product_testclient: TestClient) -> None:
    """Test adding of product"""
    _ = dbinstance
    resp = product_testclient.get("/api/v1/interop/authz")
    assert resp.status_code == 200
    parsed = ProductAuthzResponse.model_validate_json(resp.text)
    assert parsed
    assert parsed.type == "basic"
    assert parsed.username == "fake.localmaeher.dev.pvarki.fi"
    assert parsed.token is None
