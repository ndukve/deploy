"""package level stuff, like version etc"""

import logging

from fastapi.testclient import TestClient

from ocsprest import __version__

LOGGER = logging.getLogger(__name__)


def test_version() -> None:
    """Make sure version matches expected"""
    assert __version__ == "1.0.7+260612"


def test_healthcheck(client: TestClient) -> None:
    """Check that healthcheck responds"""
    resp = client.get("/api/v1/healthcheck")
    assert resp.status_code == 200
