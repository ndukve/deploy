"""Test the direct orm helpers"""

import uuid

import pytest


from rmmtxauthz.db.user import User, generate_code
from rmmtxauthz.db.engine import EngineWrapper


@pytest.mark.asyncio
async def test_list_users(dbinstance: None) -> None:
    """Create some users and test the listing"""
    _ = dbinstance
    callsign = f"cs_{generate_code(6)}"
    with EngineWrapper.singleton().get_session() as session:
        dbuser = User(rmuuid=uuid.uuid4(), username=callsign)
        session.add(dbuser)
        session.commit()
        session.refresh(dbuser)
    async for user in dbuser.list():
        assert user.mtxpassword == "REDACTED"  # pragma: allowlist secret
