"""Test the config class"""

import logging

import pytest

from miniwerk.config import KeyType, MWConfig

LOGGER = logging.getLogger(__name__)


def test_defaults() -> None:
    """Test the config defaults"""
    cfg = MWConfig()  # type: ignore[call-arg]
    LOGGER.debug(f"cfg={cfg}")
    assert cfg.ci is True
    assert cfg.domain == "pytest.pvarki.fi"
    assert cfg.subdomains == "mtls"
    assert cfg.products == "fake,tak,bl,mtx,matrix,cryptpad"
    assert str(cfg.data_path) != "/data/persistent"
    assert cfg.le_email == "example@example.com"
    LOGGER.debug(f"cfg.fqdns={cfg.fqdns}")
    assert cfg.cryptpad.api_host == "rmcryptpad"  # pylint: disable=E1101
    assert cfg.cryptpad.user_host == "mtls.cryptpad"  # pylint: disable=E1101
    assert cfg.cryptpad.user_port == 4626  # pylint: disable=E1101
    LOGGER.debug(f"cfg.fqdns={cfg.fqdns}")
    assert set(cfg.fqdns) == {
        "mtls.tak.pytest.pvarki.fi",
        "tak.pytest.pvarki.fi",
        "mtls.fake.pytest.pvarki.fi",
        "fake.pytest.pvarki.fi",
        "mtls.kc.pytest.pvarki.fi",
        "kc.pytest.pvarki.fi",
        "mtls.pytest.pvarki.fi",
        "pytest.pvarki.fi",
        "mtls.bl.pytest.pvarki.fi",
        "bl.pytest.pvarki.fi",
        "mtls.mtx.pytest.pvarki.fi",
        "mtx.pytest.pvarki.fi",
        "mtls.matrix.pytest.pvarki.fi",
        "matrix.pytest.pvarki.fi",
        "cryptpad.pytest.pvarki.fi",
        "mtls.cryptpad.pytest.pvarki.fi",
        "rmcryptpad.pytest.pvarki.fi",
        "sandbox.cryptpad.pytest.pvarki.fi",
        "mtls.sandbox.cryptpad.pytest.pvarki.fi",
    }
    assert cfg.keytype is KeyType.ECDSA


def test_singleton() -> None:
    """Test the singleton fetcher"""
    assert MWConfig._singleton is None
    cfg = MWConfig.singleton()
    # Check for the classvar
    assert MWConfig._singleton is not None
    assert cfg.ci is True
    assert cfg.domain == "pytest.pvarki.fi"
    # Remove the side-effect
    MWConfig._singleton = None


def test_sub_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config of product settings via env"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_RASENMAEHER__API_PORT", "4439")
        mpatch.setenv("MW_RASENMAEHER__USER_PORT", "4439")
        mpatch.setenv("MW_CRYPTPAD__API_HOST", "api-cryptpad")
        mpatch.setenv("MW_CRYPTPAD__API_PORT", "4631")
        mpatch.setenv("MW_CRYPTPAD__USER_HOST", "mtls.customcryptpad")
        mpatch.setenv("MW_CRYPTPAD__USER_PORT", "4632")
        mpatch.setenv("MW_KEYTYPE", "rsa")
        cfg = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug(f"cfg={cfg}")
        assert cfg.rasenmaeher.api_port == 4439  # pylint: disable=E1101  # false positive
        assert cfg.cryptpad.api_host == "api-cryptpad"  # pylint: disable=E1101
        assert cfg.cryptpad.api_port == 4631  # pylint: disable=E1101
        assert cfg.cryptpad.user_host == "mtls.customcryptpad"  # pylint: disable=E1101
        assert cfg.cryptpad.user_port == 4632  # pylint: disable=E1101
        assert cfg.keytype is KeyType.RSA


def test_kc_in_fqdns() -> None:
    """Test the singleton fetcher"""
    cfg = MWConfig.singleton()
    assert f"kc.{cfg.domain}" in cfg.fqdns
