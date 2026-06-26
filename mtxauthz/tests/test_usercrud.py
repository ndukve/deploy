"""Test the RM CRUD endpoints"""

import logging
import uuid

import pytest
from fastapi.testclient import TestClient
from libpvarki.schemas.product import UserCRUDRequest

from rmmtxauthz.db.user import User, generate_code
from rmmtxauthz.db.errors import Deleted
from rmmtxauthz.db.engine import EngineWrapper

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def crudrequest() -> UserCRUDRequest:
    """Create random user"""
    return UserCRUDRequest(
        uuid=str(uuid.uuid4()),
        callsign=f"Kissa_{generate_code(4)}",
        x509cert="-----BEGIN CERTIFICATE-----\\nMIIEwjCC...\\n-----END CERTIFICATE-----\\n",
    )


@pytest.mark.asyncio
async def test_normal_crud(
    dbinstance: None, testclient: TestClient, crudrequest: UserCRUDRequest
) -> None:
    """Test basic crud operations in order"""
    _ = dbinstance
    user = crudrequest
    payload = user.model_dump()
    resp = testclient.post("/api/v1/users/created", json=payload)
    assert resp.status_code == 200

    resp = testclient.put("/api/v1/users/updated", json=payload)
    assert resp.status_code == 200

    resp = testclient.post("/api/v1/users/promoted", json=payload)
    assert resp.status_code == 200
    dbuser = await User.by_rmuuid(user.uuid)
    assert dbuser.is_rmadmin is True

    resp = testclient.post("/api/v1/users/demoted", json=payload)
    assert resp.status_code == 200
    dbuser = await User.by_rmuuid(user.uuid)
    assert dbuser.is_rmadmin is False

    resp = testclient.post("/api/v1/users/revoked", json=payload)
    assert resp.status_code == 200

    with pytest.raises(Deleted):
        _dbuser = await User.by_rmuuid(user.uuid)


@pytest.mark.asyncio
async def test_update_wo_create(
    dbinstance: None, testclient: TestClient, crudrequest: UserCRUDRequest
) -> None:
    """Test transparent create on update"""
    _ = dbinstance
    user = crudrequest
    resp = testclient.put("/api/v1/users/updated", json=user.model_dump())
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_promote_wo_create(
    dbinstance: None, testclient: TestClient, crudrequest: UserCRUDRequest
) -> None:
    """Test transparent create on promote"""
    _ = dbinstance
    user = crudrequest
    resp = testclient.post("/api/v1/users/promoted", json=user.model_dump())
    assert resp.status_code == 200
    dbuser = await User.by_rmuuid(user.uuid)
    assert dbuser.is_rmadmin is True


@pytest.mark.asyncio
async def test_demote_wo_create(
    dbinstance: None, testclient: TestClient, crudrequest: UserCRUDRequest
) -> None:
    """Test transparent create on demote"""
    _ = dbinstance
    user = crudrequest
    with EngineWrapper.singleton().get_session() as session:
        dbuser = User(
            rmuuid=user.uuid,
            is_rmadmin=True,
            username=user.callsign,
        )
        session.add(dbuser)
        session.commit()
        session.refresh(dbuser)
    resp = testclient.post("/api/v1/users/demoted", json=user.model_dump())
    assert resp.status_code == 200
    dbuser = await User.by_rmuuid(user.uuid)
    assert dbuser.is_rmadmin is False


@pytest.mark.asyncio
async def test_unauth_crud(
    dbinstance: None, unauth_testclient: TestClient, crudrequest: UserCRUDRequest
) -> None:
    """Test basic crud operations in order"""
    _ = dbinstance
    user = crudrequest
    payload = user.model_dump()
    resp = unauth_testclient.post("/api/v1/users/created", json=payload)
    assert resp.status_code == 403

    resp = unauth_testclient.put("/api/v1/users/updated", json=payload)
    assert resp.status_code == 403

    resp = unauth_testclient.post("/api/v1/users/promoted", json=payload)
    assert resp.status_code == 403

    resp = unauth_testclient.post("/api/v1/users/demoted", json=payload)
    assert resp.status_code == 403

    resp = unauth_testclient.post("/api/v1/users/revoked", json=payload)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_proxy_disallow(
    dbinstance: None, testclient: TestClient, crudrequest: UserCRUDRequest
) -> None:
    """Test transparent create on update"""
    _ = dbinstance
    user = crudrequest
    testclient.headers.update(
        {
            "X-Rasenmaeher-Proxy": "productproxy",
            "X-Proxy-Callsign": user.callsign,
        }
    )
    resp = testclient.post("/api/v1/users/promoted", json=user.model_dump())
    assert resp.status_code == 403
