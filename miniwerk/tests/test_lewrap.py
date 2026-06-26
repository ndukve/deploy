"""Test the LW wrapper (what little we can)"""

import logging

import pytest

from miniwerk.config import MWConfig
from miniwerk.lewrap import call_certbot

LOGGER = logging.getLogger(__name__)


def check_common_args(args: list[str], config: MWConfig) -> None:
    """Common checks"""
    LOGGER.debug(f"args={args}")
    assert ",".join(config.fqdns) in args
    assert "--no-eff-email" in args
    assert "--agree-tos" in args
    assert "--cert-name" in args
    assert args[0] == "certonly"
    assert config.le_email in args
    assert "rasenmaeher" in args


@pytest.mark.asyncio
async def test_default_config() -> None:
    """Test with default config"""
    config = MWConfig()  # type: ignore[call-arg]
    LOGGER.debug(f"config={config}")
    assert config.ci is True
    _, args = await call_certbot(config)
    check_common_args(args, config)
    assert "--staging" in args
    assert "--key-type" in args
    assert "ecdsa" in args


@pytest.mark.asyncio
async def test_rsa_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_KEYTYPE", "rsa")
        config = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug(f"config={config}")
        assert config.ci is True
        _, args = await call_certbot(config)
        check_common_args(args, config)
        assert "--staging" in args
        assert "--key-type" in args
        assert "rsa" in args


@pytest.mark.asyncio
async def test_live_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_LE_TEST", "false")
        config = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug(f"config={config}")
        assert config.ci is True
        _, args = await call_certbot(config)
        check_common_args(args, config)
        assert "--staging" not in args
