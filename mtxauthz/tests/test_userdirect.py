"""Direct user routes"""

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .test_mediamtx import valid_user  # noqa F401

from rmmtxauthz.db.user import User
from rmmtxauthz.config import RMMTXSettings


LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def user_testclient(app_instance: FastAPI, valid_user: User) -> TestClient:  # noqa F811
    """Testclient with user DN"""
    client = TestClient(app_instance)
    client.headers["X-ClientCert-DN"] = f"CN={valid_user.username},O=N/A"
    return client


def test_srt(user_testclient: TestClient) -> None:
    """SRT passwords"""
    client = user_testclient
    resp = client.get(
        "/api/v1/direct/srt_default",
    )
    payload = resp.json()
    cnf = RMMTXSettings.singleton()
    assert payload["publish"] == cnf.srt_pub_password
    assert payload["read"] == cnf.srt_read_password


def test_credentials(user_testclient: TestClient, valid_user: User) -> None:  # noqa F811
    """SRT passwords"""
    client = user_testclient
    resp = client.get(
        "/api/v1/direct/credentials",
    )
    payload = resp.json()
    assert payload["username"] == valid_user.username
    assert payload["password"] == valid_user.mtxpassword
    assert payload["stream_ro_password"] == valid_user.stream_ro_password
