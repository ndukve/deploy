"""Test the HTML fragment"""

from typing import Dict
import logging


import pytest
from fastapi.testclient import TestClient

from .conftest import APP

LOGGER = logging.getLogger(__name__)
pytestmark = pytest.mark.skip(
    reason="tests need complete refactoring and most of them can't work without working RASENMAHER instance anymore",
)


def test_unauth(norppa11: Dict[str, str]) -> None:
    """Check that unauth call to auth endpoint fails"""
    client = TestClient(APP)
    resp = client.post("/api/v1/clients/fragment", json=norppa11)
    assert resp.status_code == 403


def test_get_fragment(norppa11: Dict[str, str], mtlsclient: TestClient) -> None:
    """Check that getting fragment works"""
    resp = mtlsclient.post("/api/v1/clients/fragment", json=norppa11)
    assert resp.status_code == 200
    payload = resp.json()
    assert "html" in payload
    assert payload["html"] == "<p>Hello NORPPA11a!</p>"


def test_get_admin_fragment(mtlsclient: TestClient) -> None:
    """Check that getting admin fragment works"""
    resp = mtlsclient.get("/api/v1/admins/fragment")
    assert resp.status_code == 200
    payload = resp.json()
    assert "html" in payload
    assert payload["html"] == "<p>Hello to the admin</p>"
