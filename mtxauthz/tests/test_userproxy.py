"""Proxied user routes"""

import logging

import pytest
from fastapi.testclient import TestClient
from libpvarki.schemas.product import UserCRUDRequest

from rmmtxauthz.db.user import User
from rmmtxauthz.config import RMMTXSettings

from .test_mediamtx import valid_user  # noqa F401

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def usercrud(valid_user: User) -> UserCRUDRequest:  # noqa F811
    """post payload for the proxied requetss"""
    return UserCRUDRequest(
        uuid=str(valid_user.rmuuid),
        callsign=valid_user.username,
        x509cert="-----BEGIN CERTIFICATE-----\\nMIIEwjCC...\\n-----END CERTIFICATE-----\\n",
    )


def test_srt(testclient: TestClient, usercrud: UserCRUDRequest) -> None:
    """SRT passwords"""
    resp = testclient.post("/api/v1/proxy/srt_default", json=usercrud.model_dump())
    payload = resp.json()
    LOGGER.debug(payload)
    cnf = RMMTXSettings.singleton()
    assert payload["publish"] == cnf.srt_pub_password
    assert payload["read"] == cnf.srt_read_password


def test_credentials(
    testclient: TestClient,
    valid_user: User,  # noqa F811
    usercrud: UserCRUDRequest,
) -> None:
    """SRT passwords"""
    resp = testclient.post("/api/v1/proxy/credentials", json=usercrud.model_dump())
    payload = resp.json()
    LOGGER.debug(payload)
    assert payload["username"] == valid_user.username
    assert payload["password"] == valid_user.mtxpassword
    assert payload["stream_ro_password"] == valid_user.stream_ro_password
