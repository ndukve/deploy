"""pytest automagics"""

pytest_plugins = ["libadvian.testhelpers"]

from typing import Generator  # noqa: E402
import logging  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from libadvian.logging import init_logging  # noqa: E402

from ocsprest.routes import get_app  # noqa: E402

init_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="session")
def default_env(
    monkeysession: pytest.MonkeyPatch, nice_tmpdir_ses: str
) -> Generator[None, None, None]:
    """Setup some default environment variables"""
    datadir = Path(nice_tmpdir_ses) / "data"
    cadir = datadir / "ca_public"
    cadir.mkdir(parents=True, exist_ok=True)
    crlfile = cadir / "crl.der"
    with monkeysession.context() as mpatch:
        crlfile.write_text("DUMMY")
        mpatch.setenv("CI", "true")
        mpatch.setenv("OR_DATA_PATH", str(datadir))
        mpatch.setenv("OR_CFSSL", "fakessl")
        mpatch.setenv("OR_CRL", str(crlfile))
        yield None


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Client with app instance"""
    client = TestClient(get_app())
    yield client
