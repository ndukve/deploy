"""Test helpers for rmcryptpad."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

import asyncio
import datetime
import shutil
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pytest_docker.plugin import Services


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


def build_cert_pem(common_name: str) -> str:
    """Generate a self-signed certificate PEM for testing."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(
            datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
        )
        .not_valid_after(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
        )
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def rm_headers() -> dict[str, str]:
    """Return mTLS headers simulating the Rasenmaeher control plane."""
    return {"X-ClientCert-DN": "CN=rasenmaeher,O=RM", "X-SSL-Client-Verify": "SUCCESS"}


def make_user_payload(callsign: str) -> dict[str, str]:
    """Build a user CRUD request body with a fresh certificate."""
    return {
        "uuid": f"uuid-{callsign}",
        "callsign": callsign,
        "x509cert": build_cert_pem(callsign),
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Point pytest-docker at the local test compose file."""
    return str(ROOT / "tests" / "docker-compose.yml")


@pytest.fixture(scope="session", autouse=True)
def session_env_config() -> Generator[None, None, None]:
    """Shared env defaults for rmcryptpad tests."""
    patch = pytest.MonkeyPatch()
    oidc_key_dir = ROOT / ".pytest-oidc"
    patch.setenv("RMCRYPTPAD_DATABASE_PASSWORD", "rmcryptpadtestpwd")
    patch.setenv("RMCRYPTPAD_DATABASE_USER", "rmcryptpad")
    patch.setenv("RMCRYPTPAD_DATABASE_DATABASE", "rmcryptpad")
    patch.setenv("RMCRYPTPAD_DATABASE_DRIVER", "postgresql+psycopg2")
    patch.setenv("RMCRYPTPAD_OIDC_KEY_DIR", str(oidc_key_dir))
    patch.setenv("RMCRYPTPAD_OIDC_ISSUER", "https://rmcryptpad.localhost:8443")
    patch.setenv("RMCRYPTPAD_OIDC_CLIENT_ID", "cryptpad")
    patch.setenv("RMCRYPTPAD_OIDC_CLIENT_SECRET", "cryptpad-secret")
    patch.setenv("RMCRYPTPAD_OIDC_CODE_TTL_SECONDS", "300")
    patch.setenv("RMCRYPTPAD_OIDC_TOKEN_TTL_SECONDS", "3600")
    yield None
    shutil.rmtree(oidc_key_dir, ignore_errors=True)
    patch.undo()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def dbinstance(
    docker_ip: str,
    docker_services: Services,
    session_env_config: None,
) -> AsyncGenerator[None, None]:
    """Start the test database and initialize the schema."""
    _ = session_env_config
    patch = pytest.MonkeyPatch()
    try:
        patch.setenv("RMCRYPTPAD_DATABASE_HOST", docker_ip)
        patch.setenv(
            "RMCRYPTPAD_DATABASE_PORT", str(docker_services.port_for("postgres", 5432))
        )
        from rmcryptpad.config import (  # pylint: disable=import-outside-toplevel
            DBSettings,
        )
        from rmcryptpad.oidc.keys import (  # pylint: disable=import-outside-toplevel
            OIDCKeyManager,
        )
        from rmcryptpad.db.engine import (  # pylint: disable=import-outside-toplevel
            EngineWrapper,
        )

        DBSettings._singleton = None  # pylint: disable=protected-access
        EngineWrapper._singleton = None  # pylint: disable=protected-access
        OIDCKeyManager._singleton = None  # pylint: disable=protected-access
        await asyncio.sleep(1.0)
        from rmcryptpad.db.dbinit import (  # pylint: disable=import-outside-toplevel
            drop_db,
            init_db,
        )

        await init_db()
        yield None
        await drop_db()
    finally:
        patch.undo()
