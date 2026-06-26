"""Test the mediamtx routes"""

from typing import Generator
import logging
import uuid
import json


import pytest
from fastapi.testclient import TestClient

from rmmtxauthz.db.user import User, generate_code
from rmmtxauthz.db.engine import EngineWrapper
from rmmtxauthz.mediamtx import MediaMTXControl
from rmmtxauthz.config import RMMTXSettings

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def valid_user(dbinstance: None) -> Generator[User, None, None]:
    """A valid user"""
    _ = dbinstance
    with EngineWrapper.singleton().get_session() as session:
        dbuser = User(
            rmuuid=str(uuid.uuid4()),
            username=f"koira_{generate_code(4)}",
        )
        session.add(dbuser)
        session.commit()
        session.refresh(dbuser)
        yield dbuser
        session.delete(dbuser)
        session.commit()


@pytest.fixture(scope="module")
def another_valid_user(dbinstance: None) -> Generator[User, None, None]:
    """A different valid user"""
    _ = dbinstance
    with EngineWrapper.singleton().get_session() as session:
        dbuser = User(
            rmuuid=str(uuid.uuid4()),
            username=f"mayra_{generate_code(4)}",
        )
        session.add(dbuser)
        session.commit()
        session.refresh(dbuser)
        yield dbuser
        session.delete(dbuser)
        session.commit()


def test_no_password(unauth_testclient: TestClient) -> None:
    """Test without password"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth", json={"user": "", "password": ""}
    )
    assert resp.status_code == 401


def test_wrong_password(unauth_testclient: TestClient, valid_user: User) -> None:
    """Test without password"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": "wrongpassword",  # pragma: allowlist secret
        },
    )
    assert resp.status_code == 403


def test_real_data(unauth_testclient: TestClient, valid_user: User) -> None:
    """See what gives with this real request"""
    content = '{"action":"read","id":"e14b6658-fa32-4a21-b0ac-ab1bc135dcf6","ip":"185.11.209.242","password":"__PASSWORD__","path":"live/icu/Eetu2","protocol":"srt","query":"","user":"__USERNAME__"}'.replace(  # pragma: allowlist secret
        "__USERNAME__",
        valid_user.username,
    ).replace(
        "__PASSWORD__",
        valid_user.mtxpassword,  # pragma: allowlist secret
    )
    payload = json.loads(content)
    LOGGER.debug("POSTing '{}'".format(payload))
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json=payload,
    )
    assert resp.status_code == 204


def test_wrong_username(unauth_testclient: TestClient, valid_user: User) -> None:
    """Test without password"""
    _ = valid_user
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": "nosuchuser",
            "password": "wrongpassword",  # pragma: allowlist secret
            "action": "read",
        },
    )
    assert resp.status_code == 403


def test_right_password(unauth_testclient: TestClient, valid_user: User) -> None:
    """Test with password"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.mtxpassword,
            "action": "read",
            "path": "whatever/should/not/care",
        },
    )
    assert resp.status_code == 204
    resp2 = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.stream_ro_password,
            "action": "playback",
            "path": f"live/icu/{valid_user.username}",
        },
    )
    assert resp2.status_code == 204


# NOTE: Our ENV monkeypatches have not taken affect at the time parametrize runs
@pytest.mark.parametrize(
    "path_prefix",
    [
        pytest.param(path_prefix, id=path_prefix)
        for path_prefix in RMMTXSettings.singleton().user_paths
    ],
)
def test_publish_valid_path(
    unauth_testclient: TestClient, valid_user: User, path_prefix: str
) -> None:
    """Test valid user paths"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.mtxpassword,
            "path": f"{path_prefix}/{valid_user.username}",
            "action": "publish",
        },
    )
    assert resp.status_code == 204
    resp2 = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.mtxpassword,
            "path": f"{path_prefix}/{valid_user.username}/more",
            "action": "publish",
        },
    )
    assert resp2.status_code == 204
    resp3 = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.stream_ro_password,
            "path": f"{path_prefix}/{valid_user.username}",
            "action": "publish",
        },
    )
    assert resp3.status_code == 403


@pytest.mark.parametrize(
    "path_prefix",
    [
        pytest.param(path_prefix, id=path_prefix)
        for path_prefix in RMMTXSettings.singleton().user_paths
    ],
)
def test_readonly_valid_path(
    unauth_testclient: TestClient, valid_user: User, path_prefix: str
) -> None:
    """Test playing a stream with RO password"""
    for action in ("read", "playback"):
        resp = unauth_testclient.post(
            "/api/v1/mediamtx/auth",
            json={
                "user": valid_user.username,
                "password": valid_user.stream_ro_password,
                "path": f"{path_prefix}/{valid_user.username}",
                "action": action,
            },
        )
        assert resp.status_code == 204


def test_read_any_path(unauth_testclient: TestClient, valid_user: User) -> None:
    """Test that any path can be read"""
    for action in ("read", "playback"):
        resp = unauth_testclient.post(
            "/api/v1/mediamtx/auth",
            json={
                "user": valid_user.username,
                "password": valid_user.mtxpassword,
                "path": f"/somethingrandom/{uuid.uuid4()}",
                "action": action,
            },
        )
        assert resp.status_code == 204


# NOTE: Our ENV monkeypatches have not taken affect at the time parametrize runs
@pytest.mark.parametrize(
    "prefix", [pytest.param(prefix, id=prefix) for prefix in ("live", "undead")]
)
def test_publish_path_wrong_tool(
    unauth_testclient: TestClient, valid_user: User, prefix: str
) -> None:
    """Test invalid tool but otherwise fine"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.mtxpassword,
            "path": f"{prefix}/nosuchtool/{valid_user.username}",
            "action": "publish",
        },
    )
    assert resp.status_code == 403


# NOTE: Our ENV monkeypatches have not taken affect at the time parametrize runs
@pytest.mark.parametrize(
    "tool", [pytest.param(tool, id=tool) for tool in RMMTXSettings.singleton().tools]
)
def test_publish_path_wrong_prefix(
    unauth_testclient: TestClient, valid_user: User, tool: str
) -> None:
    """Test invalid tool but otherwise fine"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.mtxpassword,
            "path": f"nosuchprefix/{tool}/{valid_user.username}",
            "action": "publish",
        },
    )
    assert resp.status_code == 403


# NOTE: Our ENV monkeypatches have not taken affect at the time parametrize runs
@pytest.mark.parametrize(
    "path_prefix",
    [
        pytest.param(prefix, id=prefix)
        for prefix in RMMTXSettings.singleton().user_paths
    ],
)
def test_publish_path_wrong_callsign(
    unauth_testclient: TestClient,
    valid_user: User,
    path_prefix: str,
    another_valid_user: User,
) -> None:
    """Test valid user paths"""
    resp = unauth_testclient.post(
        "/api/v1/mediamtx/auth",
        json={
            "user": valid_user.username,
            "password": valid_user.mtxpassword,
            "path": f"{path_prefix}/{another_valid_user.username}",
            "action": "publish",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_srt_lowlevel() -> None:
    """Test the API wrapper SRT password method"""
    api = MediaMTXControl.singleton()
    result = await api.ensure_srt_pass()
    assert result
    # Try it again
    result = await api.ensure_srt_pass()
    assert result
